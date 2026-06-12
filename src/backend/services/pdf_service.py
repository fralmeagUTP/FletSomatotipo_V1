from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
import struct
import zlib

from src.frontend.assets import ASSETS_DIR, REFERENCE_IMAGES
from src.frontend.somatocarta import (
    CHART_HEIGHT as SOMATOCARTA_CHART_HEIGHT,
    CHART_WIDTH as SOMATOCARTA_CHART_WIDTH,
    SOURCE_HEIGHT as SOMATOCARTA_SOURCE_HEIGHT,
    SOURCE_WIDTH as SOMATOCARTA_SOURCE_WIDTH,
    coordinate_to_pixel as somatocarta_coordinate_to_pixel,
    parse_coordinate as parse_somatocarta_coordinate,
)


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT_MARGIN = 42
LINE_COLOR = "#2f2f2f"
MUTED_COLOR = "#666666"
PRIMARY_COLOR = "#2e5cb8"
LIGHT_BLUE = "#e8f0fe"
LIGHT_GRAY = "#f3f5f8"
TABLE_LINE = "#d7dce3"
SUCCESS_COLOR = "#00a86b"
WARNING_COLOR = "#f59e0b"


LONGITUDINAL_REPORT_METRICS = [
    ("Peso", "PESO_kg", "kg"),
    ("IMC", "IMC", ""),
    ("Grasa Yuhasz", "PorcRasoYuasz", "%"),
    ("Masa muscular", "Mma", "kg"),
    ("Endomorfismo", "Endomorfismo", ""),
    ("Mesomorfismo", "Mesomorfismo", ""),
    ("Ectomorfismo", "Ectomorfismo", ""),
]


ATHLETE_FIELDS = [
    ("Deportista", "NOMBRE_DEPORTISTA"),
    ("Identificación", "IDENTI_DEPORTISTA"),
    ("Fecha valoración", "FECHA_MEDIDA"),
    ("Edad", "EDAD"),
    ("Sexo", "SEXO_DEPORTISTA"),
]

KEY_METRICS = [
    ("Peso", "PESO_kg", "kg"),
    ("Estatura", "ESTA_USER_CM", "cm"),
    ("IMC", "IMC", ""),
    ("Estado IMC", "EstadoIMC", ""),
]

SOMATOTYPE_FIELDS = [
    ("Endomorfismo", "Endomorfismo", "EscalaEndomorfismo"),
    ("Mesomorfismo", "Mesomorfismo", "EscalaMesomorfismo"),
    ("Ectomorfismo", "Ectomorfismo", "EscalaEctomorfismo"),
]

COMPOSITION_FIELDS = [
    ("Porc. graso Yuhasz", "PorcRasoYuasz", "%"),
    ("Peso graso Yuhasz", "PesoRasoYuazs", "kg"),
    ("Porc. graso Faulkner", "PorcGrasoFaulker", "%"),
    ("Peso graso Faulkner", "PesoRasoFaulker", "kg"),
    ("Porc. graso Johnston", "PorcGrasoJonson", "%"),
    ("Peso graso Johnston", "PesoGrasoJhonston", "kg"),
    ("Peso óseo", "PesoOseo", "kg"),
    ("Peso residual", "PesoResidual", "kg"),
    ("Masa muscular", "Mma", "kg"),
]

MEASUREMENT_FIELDS = [
    ("Pliegue tricipital", "PLIEGUE_TRICIPITAL", "mm"),
    ("Pliegue subescapular", "PLIEGUE_SUBESCAPULAR", "mm"),
    ("Pliegue suprailiaco", "PLIEGUE_SUPRAILIACO", "mm"),
    ("Pliegue abdominal", "PLIEGUE_ABDOMINAL", "mm"),
    ("Pliegue muslo anterior", "PLIEGUE_MUSLO_ANT", "mm"),
    ("Pliegue medial pierna", "PLIEGUE_MEDIAL_PIERNA", "mm"),
    ("Diámetro muñeca", "DIAMETRO_BIEPI_MUNECA", "mm"),
    ("Diámetro fémur", "DIAMETRO_BIEPI_FEMUR", "mm"),
    ("Diámetro codo", "DIAMETRO_CODO", "mm"),
    ("Perímetro bíceps contraído", "PERIMETRO_BICED_CONTRAIDO", "cm"),
    ("Perímetro pierna", "PERIMETRO_PIERNA", "cm"),
    ("Circunferencia carpo", "CIRCUNFERENCIA_CARPO", "cm"),
]


def display_value(value):
    if value is None:
        return "---"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def record_value(record, field, default=None):
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def parse_pdf_number(value):
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value).replace(",", ".")))
    except Exception:
        return None


def sort_records_by_date(records):
    return sorted(
        records,
        key=lambda record: (
            str(record_value(record, "FECHA_MEDIDA", "")),
            record_value(record, "id_Somatotipo", 0) or 0,
        ),
    )


def build_pdf_metric_series(records, field):
    series = []
    for index, record in enumerate(sort_records_by_date(records), start=1):
        value = parse_pdf_number(record_value(record, field))
        if value is None:
            continue
        series.append(
            {
                "index": index,
                "value": value,
                "date": str(record_value(record, "FECHA_MEDIDA", "")),
            }
        )
    return series


def longitudinal_delta_text(series, unit=""):
    if len(series) < 2:
        return "Sin tendencia"
    delta = series[-1]["value"] - series[0]["value"]
    sign = "+" if delta > 0 else ""
    suffix = f" {unit}" if unit else ""
    return f"{sign}{delta:.2f}{suffix}"


def short_text(value, max_chars=34):
    text = display_value(value)
    if ":" in text:
        text = text.split(":", 1)[0].strip()
    if "." in text and len(text) > max_chars:
        text = text.split(".", 1)[0].strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) / 255 for index in (0, 2, 4))


def escape_pdf_text(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def color_command(color, stroke=False):
    red, green, blue = hex_to_rgb(color)
    operator = "RG" if stroke else "rg"
    return f"{red:.3f} {green:.3f} {blue:.3f} {operator}"


def text_command(x, y, text, size=10, color=LINE_COLOR, font="F1"):
    return (
        f"q {color_command(color)} "
        f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({escape_pdf_text(text)}) Tj ET Q"
    )


def line_command(x1, y1, x2, y2, stroke=0.8, color=LINE_COLOR):
    return f"q {color_command(color, stroke=True)} {stroke} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q"


def rect_command(x, y, width, height, fill=None, stroke=None, stroke_width=0.8):
    commands = ["q"]
    if fill:
        commands.append(color_command(fill))
        commands.append(f"{x:.2f} {y:.2f} {width:.2f} {height:.2f} re f")
    if stroke:
        commands.append(color_command(stroke, stroke=True))
        commands.append(f"{stroke_width} w {x:.2f} {y:.2f} {width:.2f} {height:.2f} re S")
    commands.append("Q")
    return " ".join(commands)


def circle_command(x, y, radius, fill="#ff0000", stroke="#000000"):
    control = radius * 0.5522847498
    path = (
        f"{x + radius:.2f} {y:.2f} m "
        f"{x + radius:.2f} {y + control:.2f} {x + control:.2f} {y + radius:.2f} {x:.2f} {y + radius:.2f} c "
        f"{x - control:.2f} {y + radius:.2f} {x - radius:.2f} {y + control:.2f} {x - radius:.2f} {y:.2f} c "
        f"{x - radius:.2f} {y - control:.2f} {x - control:.2f} {y - radius:.2f} {x:.2f} {y - radius:.2f} c "
        f"{x + control:.2f} {y - radius:.2f} {x + radius:.2f} {y - control:.2f} {x + radius:.2f} {y:.2f} c"
    )
    return f"q {color_command(fill)} {path} f {color_command(stroke, stroke=True)} 0.8 w {path} S Q"


def image_command(image_name, x, y, width, height):
    return f"q {width:.2f} 0 0 {height:.2f} {x:.2f} {y:.2f} cm /{image_name} Do Q"


def value_from_record(record, field):
    return display_value(getattr(record, field, None))


def value_with_unit(record, field, unit=""):
    value = value_from_record(record, field)
    if not unit or value == "---":
        return value
    return f"{value} {unit}"


def append_header(commands, title, subtitle=None):
    commands.append(rect_command(0, PAGE_HEIGHT - 82, PAGE_WIDTH, 82, fill=PRIMARY_COLOR))
    commands.append(text_command(LEFT_MARGIN, 800, title, 18, color="#ffffff", font="F2"))
    if subtitle:
        commands.append(text_command(LEFT_MARGIN, 780, subtitle, 9, color="#ffffff"))


def append_section_title(commands, x, y, title):
    commands.append(text_command(x, y, title, 12, color=PRIMARY_COLOR, font="F2"))
    commands.append(line_command(x, y - 5, x + 235, y - 5, color=TABLE_LINE))


def append_info_card(commands, record, x, y, width, height):
    commands.append(rect_command(x, y - height, width, height, fill=LIGHT_GRAY, stroke=TABLE_LINE))
    commands.append(text_command(x + 14, y - 22, "Datos del deportista", 12, color=PRIMARY_COLOR, font="F2"))
    row_y = y - 44
    for label, field in ATHLETE_FIELDS:
        commands.append(text_command(x + 14, row_y, f"{label}:", 8, color=MUTED_COLOR))
        commands.append(text_command(x + 118, row_y, short_text(value_from_record(record, field), 32), 9, font="F2"))
        row_y -= 18


def append_metric_cards(commands, record, x, y):
    card_width = 126
    card_height = 52
    for index, (label, field, unit) in enumerate(KEY_METRICS):
        card_x = x + ((index % 2) * (card_width + 8))
        card_y = y - ((index // 2) * (card_height + 10))
        value = value_with_unit(record, field, unit)
        commands.append(rect_command(card_x, card_y - card_height, card_width, card_height, fill="#ffffff", stroke=TABLE_LINE))
        commands.append(text_command(card_x + 10, card_y - 17, label, 8, color=MUTED_COLOR))
        commands.append(text_command(card_x + 10, card_y - 37, short_text(value, 18), 13, color=PRIMARY_COLOR, font="F2"))


def append_somatotype_summary(commands, record, x, y):
    append_section_title(commands, x, y, "Somatotipo")
    row_y = y - 28
    for label, value_field, scale_field in SOMATOTYPE_FIELDS:
        value = value_from_record(record, value_field)
        scale = short_text(getattr(record, scale_field, None), 42)
        commands.append(rect_command(x, row_y - 18, 238, 24, fill="#ffffff", stroke=TABLE_LINE))
        commands.append(text_command(x + 10, row_y - 10, label, 8, color=MUTED_COLOR))
        commands.append(text_command(x + 112, row_y - 10, value, 10, font="F2"))
        commands.append(text_command(x + 152, row_y - 10, scale, 8, color=MUTED_COLOR))
        row_y -= 28
    extra_rows = [
        ("Complexión", "Complexion", "TipoComplexion"),
        ("Coordenada X", "X", None),
        ("Coordenada Y", "Y", None),
    ]
    for label, value_field, detail_field in extra_rows:
        value = value_from_record(record, value_field)
        detail = short_text(getattr(record, detail_field, None), 32) if detail_field else ""
        commands.append(rect_command(x, row_y - 18, 238, 24, fill="#ffffff", stroke=TABLE_LINE))
        commands.append(text_command(x + 10, row_y - 10, label, 8, color=MUTED_COLOR))
        commands.append(text_command(x + 112, row_y - 10, value, 10, font="F2"))
        if detail:
            commands.append(text_command(x + 152, row_y - 10, detail, 8, color=MUTED_COLOR))
        row_y -= 28


def append_table(commands, title, fields, record, x, y, width=240, row_height=20):
    append_section_title(commands, x, y, title)
    row_y = y - 28
    commands.append(rect_command(x, row_y - row_height + 5, width, row_height, fill=LIGHT_BLUE, stroke=TABLE_LINE, stroke_width=0.4))
    commands.append(text_command(x + 8, row_y - 8, "Parámetro", 8, color=PRIMARY_COLOR, font="F2"))
    commands.append(text_command(x + width - 96, row_y - 8, "Valor", 8, color=PRIMARY_COLOR, font="F2"))
    commands.append(text_command(x + width - 36, row_y - 8, "Unidad", 8, color=PRIMARY_COLOR, font="F2"))
    row_y -= row_height
    for index, (label, field, unit) in enumerate(fields):
        fill = "#ffffff" if index % 2 == 0 else LIGHT_GRAY
        commands.append(rect_command(x, row_y - row_height + 5, width, row_height, fill=fill, stroke=TABLE_LINE, stroke_width=0.4))
        commands.append(text_command(x + 8, row_y - 8, short_text(label, 25), 8, color=MUTED_COLOR))
        commands.append(text_command(x + width - 96, row_y - 8, short_text(value_from_record(record, field), 14), 9, font="F2"))
        commands.append(text_command(x + width - 34, row_y - 8, unit, 8, color=MUTED_COLOR))
        row_y -= row_height
    return row_y


def coordinate_to_pdf_point(x_value, y_value, left=330, bottom=390, width=210, height=300):
    x_min, x_max = -8, 8
    y_min, y_max = -10, 16
    x = left + ((float(x_value) - x_min) / (x_max - x_min)) * width
    y = bottom + ((float(y_value) - y_min) / (y_max - y_min)) * height
    return x, y


def append_arc(commands, left, bottom, width, height):
    points = []
    x_value = -8
    while x_value <= 8:
        y_value = 14 - (0.049 * (x_value**2))
        points.append(coordinate_to_pdf_point(x_value, y_value, left, bottom, width, height))
        x_value += 0.5
    for start, end in zip(points, points[1:]):
        commands.append(line_command(start[0], start[1], end[0], end[1], stroke=1.0))


def append_somatocarta(commands, record):
    left, bottom, width, height = 318, 372, 230, 318
    right = left + width
    top = bottom + height
    origin_x, origin_y = coordinate_to_pdf_point(0, 0, left, bottom, width, height)

    commands.append(text_command(left + 72, top + 22, "Somatocarta", 12, color=PRIMARY_COLOR, font="F2"))
    commands.append(rect_command(left, bottom, width, height, fill="#ffffff", stroke=LINE_COLOR))
    commands.append(line_command(left, origin_y, right, origin_y, stroke=1.0))
    commands.append(line_command(origin_x, bottom, origin_x, top, stroke=1.0))
    commands.append(line_command(*coordinate_to_pdf_point(-5, -6.5, left, bottom, width, height), *coordinate_to_pdf_point(0, 0, left, bottom, width, height), stroke=1.0))
    commands.append(line_command(*coordinate_to_pdf_point(0, 0, left, bottom, width, height), *coordinate_to_pdf_point(5, -6.5, left, bottom, width, height), stroke=1.0))
    commands.append(line_command(*coordinate_to_pdf_point(-3, 4.5, left, bottom, width, height), *coordinate_to_pdf_point(0, 0, left, bottom, width, height), stroke=1.0))
    commands.append(line_command(*coordinate_to_pdf_point(0, 0, left, bottom, width, height), *coordinate_to_pdf_point(3, 4.5, left, bottom, width, height), stroke=1.0))
    append_arc(commands, left, bottom, width, height)

    for tick in range(-8, 9, 4):
        tick_x, _ = coordinate_to_pdf_point(tick, 0, left, bottom, width, height)
        commands.append(text_command(tick_x - 7, top + 6, f"{tick:+d}", 7, color=MUTED_COLOR))
    for tick in range(-10, 17, 4):
        _, tick_y = coordinate_to_pdf_point(0, tick, left, bottom, width, height)
        commands.append(text_command(left - 20, tick_y - 2, f"{tick:+d}", 7, color=MUTED_COLOR))

    commands.append(text_command(origin_x - 34, top - 46, "MESO", 8, font="F2"))
    commands.append(text_command(left + 12, bottom + 22, "ENDO", 8, font="F2"))
    commands.append(text_command(right - 43, bottom + 22, "ECTO", 8, font="F2"))

    x_value = getattr(record, "X", None)
    y_value = getattr(record, "Y", None)
    if x_value is not None and y_value is not None:
        point_x, point_y = coordinate_to_pdf_point(x_value, y_value, left, bottom, width, height)
        commands.append(circle_command(point_x, point_y, 4.2, fill="#ff0000", stroke="#000000"))
        commands.append(text_command(point_x + 8, point_y - 3, short_text(getattr(record, "NOMBRE_DEPORTISTA", "Deportista"), 18), 8, color="#ff0000"))
    commands.append(text_command(left, bottom - 18, f"X: {value_from_record(record, 'X')}   Y: {value_from_record(record, 'Y')}", 8, color=MUTED_COLOR))


def paeth_predictor(left, above, upper_left):
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def decode_png_rgb(path):
    data = Path(path).read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"El archivo no es PNG: {path}")

    offset = 8
    width = height = bit_depth = color_type = None
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if bit_depth != 8 or color_type not in (0, 2, 4, 6):
        raise ValueError(f"PNG no soportado para PDF: bit_depth={bit_depth}, color_type={color_type}")

    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    previous = bytearray(stride)
    rows = []
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + stride])
        cursor += stride
        for index in range(stride):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                row[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                row[index] = (row[index] + above) & 0xFF
            elif filter_type == 3:
                row[index] = (row[index] + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                row[index] = (row[index] + paeth_predictor(left, above, upper_left)) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"Filtro PNG no soportado: {filter_type}")
        rows.append(row)
        previous = row

    rgb = bytearray(width * height * 3)
    target = 0
    for row in rows:
        for x in range(width):
            source = x * channels
            if color_type == 0:
                red = green = blue = row[source]
                alpha = 255
            elif color_type == 2:
                red, green, blue = row[source : source + 3]
                alpha = 255
            elif color_type == 4:
                red = green = blue = row[source]
                alpha = row[source + 1]
            else:
                red, green, blue, alpha = row[source : source + 4]
            rgb[target] = ((red * alpha) + (255 * (255 - alpha))) // 255
            rgb[target + 1] = ((green * alpha) + (255 * (255 - alpha))) // 255
            rgb[target + 2] = ((blue * alpha) + (255 * (255 - alpha))) // 255
            target += 3
    return width, height, bytes(rgb)


def downsample_rgb(width, height, rgb, max_width=900, max_height=900):
    ratio = min(max_width / width, max_height / height, 1)
    target_width = max(1, int(width * ratio))
    target_height = max(1, int(height * ratio))
    if target_width == width and target_height == height:
        return width, height, rgb

    output = bytearray(target_width * target_height * 3)
    for target_y in range(target_height):
        source_y = min(height - 1, int(target_y * height / target_height))
        for target_x in range(target_width):
            source_x = min(width - 1, int(target_x * width / target_width))
            source_index = ((source_y * width) + source_x) * 3
            target_index = ((target_y * target_width) + target_x) * 3
            output[target_index : target_index + 3] = rgb[source_index : source_index + 3]
    return target_width, target_height, bytes(output)


def load_png_image_xobject(filename, max_width=900, max_height=900):
    width, height, rgb = decode_png_rgb(ASSETS_DIR / filename)
    width, height, rgb = downsample_rgb(width, height, rgb, max_width=max_width, max_height=max_height)
    return {
        "width": width,
        "height": height,
        "data": zlib.compress(rgb, level=6),
    }


def build_report_images():
    return {
        "ImIMC": load_png_image_xobject(REFERENCE_IMAGES["imc"], max_width=520, max_height=700),
        "ImContextura": load_png_image_xobject(REFERENCE_IMAGES["contextura"], max_width=720, max_height=520),
        "ImSomatotipos": load_png_image_xobject(REFERENCE_IMAGES["somatotipos"], max_width=720, max_height=520),
        "ImSomatocarta": load_png_image_xobject(REFERENCE_IMAGES["somatocarta"], max_width=760, max_height=950),
    }


def build_pdf_document(content_streams, images=None):
    if isinstance(content_streams, bytes):
        content_streams = [content_streams]
    images = images or {}

    page_count = len(content_streams)
    page_ids = list(range(3, 3 + page_count))
    content_ids = list(range(3 + page_count, 3 + (page_count * 2)))
    f1_id = 3 + (page_count * 2)
    f2_id = f1_id + 1
    image_ids = {
        name: f2_id + index + 1
        for index, name in enumerate(images)
    }
    xobject_resources = ""
    if image_ids:
        xobject_entries = " ".join(f"/{name} {object_id} 0 R" for name, object_id in image_ids.items())
        xobject_resources = f" /XObject << {xobject_entries} >>"

    objects = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode("cp1252", errors="replace"))
    for page_id, content_id in zip(page_ids, content_ids):
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R >>{xobject_resources} >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("cp1252", errors="replace")
        )
    for stream in content_streams:
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode("cp1252", errors="replace") + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    for image in images.values():
        header = (
            f"<< /Type /XObject /Subtype /Image /Width {image['width']} /Height {image['height']} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(image['data'])} >>\n"
            "stream\n"
        ).encode("cp1252", errors="replace")
        objects.append(header + image["data"] + b"\nendstream")

    output = BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("cp1252", errors="replace"))
        output.write(obj)
        output.write(b"\nendobj\n")

    xref_position = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("cp1252", errors="replace"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("cp1252", errors="replace"))
    output.write(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("cp1252", errors="replace")
    )
    return output.getvalue()


def append_reference_image(commands, image_name, title, description, x, y, width, height):
    append_section_title(commands, x, y, title)
    box_y = y - height - 26
    commands.append(rect_command(x, box_y, width, height + 16, fill="#ffffff", stroke=TABLE_LINE))
    commands.append(image_command(image_name, x + 10, box_y + 8, width - 20, height))
    if description:
        commands.append(text_command(x + 10, box_y - 16, short_text(description, 86), 8, color=MUTED_COLOR))


def append_analysis_page(commands, record):
    append_header(commands, "Análisis de la valoración", f"Deportista: {short_text(getattr(record, 'NOMBRE_DEPORTISTA', ''), 45)}")
    commands.append(text_command(LEFT_MARGIN, 724, "Análisis IMC", 12, color=PRIMARY_COLOR, font="F2"))
    commands.append(text_command(LEFT_MARGIN, 700, "IMC:", 9, font="F2"))
    commands.append(text_command(478, 700, value_with_unit(record, "IMC", "kg/m²") + f" ({value_from_record(record, 'EstadoIMC')})", 9))
    commands.append(rect_command(LEFT_MARGIN, 672, 510, 28, fill=LIGHT_BLUE))
    commands.append(text_command(LEFT_MARGIN + 12, 655, "IMC calculado. En menores de 20 años, interpretar con referencias por edad y sexo.", 8, color=MUTED_COLOR))
    append_reference_image(
        commands,
        "ImIMC",
        "Referencia IMC",
        "Apoyo visual para interpretar el índice de masa corporal y su clasificación.",
        LEFT_MARGIN,
        618,
        210,
        266,
    )
    commands.append(text_command(300, 618, "Complexión física", 12, color=PRIMARY_COLOR, font="F2"))
    commands.append(text_command(300, 594, "Complexión:", 9, font="F2"))
    commands.append(text_command(444, 594, f"{value_from_record(record, 'Complexion')} ({value_from_record(record, 'TipoComplexion')})", 9))
    append_reference_image(
        commands,
        "ImContextura",
        "Referencia de contextura física",
        "Relaciona estatura, peso y complexión para contextualizar la valoración corporal.",
        300,
        552,
        238,
        164,
    )


def append_somatotype_page(commands, record):
    append_header(commands, "Somatotipo", f"Deportista: {short_text(getattr(record, 'NOMBRE_DEPORTISTA', ''), 45)}")
    append_reference_image(
        commands,
        "ImSomatotipos",
        "Referencia de somatotipos corporales",
        "Apoya la lectura de endomorfismo, mesomorfismo y ectomorfismo del deportista.",
        LEFT_MARGIN,
        724,
        510,
        355,
    )
    append_somatotype_summary(commands, record, LEFT_MARGIN, 320)


def append_somatocarta_asset(commands, record):
    append_header(commands, "Somatocarta", f"Deportista: {short_text(getattr(record, 'NOMBRE_DEPORTISTA', ''), 45)}")
    display_width = 500
    display_height = display_width * (SOMATOCARTA_SOURCE_HEIGHT / SOMATOCARTA_SOURCE_WIDTH)
    image_x = (PAGE_WIDTH - display_width) / 2
    image_y = 112
    commands.append(image_command("ImSomatocarta", image_x, image_y, display_width, display_height))

    x_value = parse_somatocarta_coordinate(getattr(record, "X", None))
    y_value = parse_somatocarta_coordinate(getattr(record, "Y", None))
    if x_value is not None and y_value is not None:
        point_x, point_y = somatocarta_coordinate_to_pixel(x_value, y_value)
        pdf_x = image_x + (point_x / SOMATOCARTA_CHART_WIDTH) * display_width
        pdf_y = image_y + display_height - ((point_y / SOMATOCARTA_CHART_HEIGHT) * display_height)
        commands.append(circle_command(pdf_x, pdf_y, 5.5, fill="#ff3b30", stroke="#ffffff"))
        commands.append(rect_command(pdf_x + 8, pdf_y - 9, 76, 18, fill="#fff9c9", stroke="#fff9c9"))
        commands.append(text_command(pdf_x + 14, pdf_y - 4, short_text(getattr(record, "NOMBRE_DEPORTISTA", "Deportista"), 18), 7, color="#0b2f6b", font="F2"))

    commands.append(text_command(LEFT_MARGIN, 88, f"Coordenadas: X={value_from_record(record, 'X')} · Y={value_from_record(record, 'Y')}", 9, color=MUTED_COLOR))
    commands.append(text_command(LEFT_MARGIN, 70, "La posición usa la misma calibración visual del historial corporal.", 8, color=MUTED_COLOR))


def append_longitudinal_summary_cards(commands, records, x, y):
    latest = sort_records_by_date(records)[-1] if records else None
    card_width = 120
    card_height = 58
    for index, (label, field, unit) in enumerate(LONGITUDINAL_REPORT_METRICS[:4]):
        card_x = x + ((index % 4) * (card_width + 8))
        value = record_value(latest, field) if latest else None
        series = build_pdf_metric_series(records, field)
        text = "---" if value is None else f"{display_value(value)} {unit}".strip()
        commands.append(rect_command(card_x, y - card_height, card_width, card_height, fill=LIGHT_GRAY, stroke=TABLE_LINE))
        commands.append(text_command(card_x + 10, y - 17, label, 8, color=MUTED_COLOR))
        commands.append(text_command(card_x + 10, y - 36, short_text(text, 17), 13, color=PRIMARY_COLOR, font="F2"))
        commands.append(text_command(card_x + 10, y - 50, f"Cambio: {longitudinal_delta_text(series, unit)}", 7, color=MUTED_COLOR))


def append_longitudinal_table(commands, records, x, y):
    fields = [
        ("Fecha", "FECHA_MEDIDA", ""),
        ("Peso", "PESO_kg", "kg"),
        ("IMC", "IMC", ""),
        ("Grasa Yuhasz", "PorcRasoYuasz", "%"),
        ("Masa muscular", "Mma", "kg"),
        ("X", "X", ""),
        ("Y", "Y", ""),
    ]
    widths = [74, 58, 52, 84, 88, 45, 45]
    row_height = 20
    append_section_title(commands, x, y, "Evolución registrada")
    row_y = y - 32
    commands.append(rect_command(x, row_y - row_height + 5, sum(widths), row_height, fill=LIGHT_BLUE, stroke=TABLE_LINE, stroke_width=0.4))
    column_x = x
    for (label, _, _), width in zip(fields, widths):
        commands.append(text_command(column_x + 5, row_y - 8, label, 7, color=PRIMARY_COLOR, font="F2"))
        column_x += width
    row_y -= row_height

    for index, record in enumerate(sort_records_by_date(records)[:18]):
        fill = "#ffffff" if index % 2 == 0 else LIGHT_GRAY
        commands.append(rect_command(x, row_y - row_height + 5, sum(widths), row_height, fill=fill, stroke=TABLE_LINE, stroke_width=0.4))
        column_x = x
        for (_, field, unit), width in zip(fields, widths):
            value = display_value(record_value(record, field))
            if unit and value != "---":
                value = f"{value} {unit}"
            commands.append(text_command(column_x + 5, row_y - 8, short_text(value, 15), 7, color=LINE_COLOR))
            column_x += width
        row_y -= row_height
    if len(records) > 18:
        commands.append(text_command(x, row_y - 8, f"Se muestran las primeras 18 de {len(records)} valoraciones.", 8, color=MUTED_COLOR))


def append_line_chart(commands, title, series, unit, x, y, width=220, height=130):
    append_section_title(commands, x, y, title)
    chart_bottom = y - height - 26
    chart_left = x + 32
    chart_width = width - 42
    chart_height = height - 18
    commands.append(rect_command(x, chart_bottom, width, height, fill="#ffffff", stroke=TABLE_LINE))
    if len(series) < 2:
        commands.append(text_command(x + 12, chart_bottom + height - 44, "Se requieren al menos dos valores.", 8, color=MUTED_COLOR))
        return

    values = [point["value"] for point in series]
    min_value = min(values)
    max_value = max(values)
    padding = max((max_value - min_value) * 0.15, 1)
    min_axis = min_value - padding
    max_axis = max_value + padding
    max_index = max(point["index"] for point in series)

    commands.append(line_command(chart_left, chart_bottom + 22, chart_left + chart_width, chart_bottom + 22, color=TABLE_LINE))
    commands.append(line_command(chart_left, chart_bottom + 22, chart_left, chart_bottom + 22 + chart_height, color=TABLE_LINE))
    commands.append(text_command(x + 8, chart_bottom + 24 + chart_height, f"{max_axis:.1f}", 6, color=MUTED_COLOR))
    commands.append(text_command(x + 8, chart_bottom + 18, f"{min_axis:.1f}", 6, color=MUTED_COLOR))

    points = []
    for point in series:
        point_x = chart_left + ((point["index"] - 1) / max(max_index - 1, 1)) * chart_width
        point_y = chart_bottom + 22 + ((point["value"] - min_axis) / (max_axis - min_axis)) * chart_height
        points.append((point_x, point_y, point))

    for start, end in zip(points, points[1:]):
        commands.append(line_command(start[0], start[1], end[0], end[1], stroke=1.4, color=PRIMARY_COLOR))
    for point_x, point_y, point in points:
        commands.append(circle_command(point_x, point_y, 3.2, fill=PRIMARY_COLOR, stroke="#ffffff"))
    commands.append(text_command(x + 10, chart_bottom + 8, f"{series[0]['date']} → {series[-1]['date']} · Cambio {longitudinal_delta_text(series, unit)}", 7, color=MUTED_COLOR))


def append_longitudinal_somatocarta(commands, records):
    append_header(commands, "Somatocarta longitudinal", f"{len(records)} valoración(es) graficadas")
    display_width = 460
    display_height = display_width * (SOMATOCARTA_SOURCE_HEIGHT / SOMATOCARTA_SOURCE_WIDTH)
    image_x = 36
    image_y = 138
    commands.append(image_command("ImSomatocarta", image_x, image_y, display_width, display_height))

    palette = ["#ff3b30", "#2e5cb8", "#00a86b", "#f59e0b", "#8b5cf6", "#0891b2", "#db2777", "#64748b"]
    points = []
    for record in sort_records_by_date(records):
        x_value = parse_somatocarta_coordinate(record_value(record, "X"))
        y_value = parse_somatocarta_coordinate(record_value(record, "Y"))
        if x_value is None or y_value is None:
            continue
        points.append(
            {
                "x": x_value,
                "y": y_value,
                "date": str(record_value(record, "FECHA_MEDIDA", "")),
            }
        )

    for index, point in enumerate(points):
        point_x, point_y = somatocarta_coordinate_to_pixel(point["x"], point["y"])
        pdf_x = image_x + (point_x / SOMATOCARTA_CHART_WIDTH) * display_width
        pdf_y = image_y + display_height - ((point_y / SOMATOCARTA_CHART_HEIGHT) * display_height)
        color = palette[index % len(palette)]
        commands.append(circle_command(pdf_x, pdf_y, 4.8, fill=color, stroke="#ffffff"))

    legend_x = 500
    legend_y = 708
    commands.append(text_command(legend_x, legend_y, "Coordenadas", 10, color=PRIMARY_COLOR, font="F2"))
    for index, point in enumerate(points[:24]):
        row_y = legend_y - 18 - (index * 18)
        color = palette[index % len(palette)]
        commands.append(circle_command(legend_x + 5, row_y + 3, 3.2, fill=color, stroke="#ffffff"))
        commands.append(text_command(legend_x + 14, row_y, short_text(point["date"], 12), 6, color=LINE_COLOR))
        commands.append(text_command(legend_x + 14, row_y - 8, f"X={point['x']:.2f} Y={point['y']:.2f}", 6, color=MUTED_COLOR))
    commands.append(text_command(LEFT_MARGIN, 92, "Cada punto representa una valoración corporal y su fecha de medición.", 8, color=MUTED_COLOR))


def append_athlete_info_card(commands, athlete_info, x, y, width, height):
    """
    Agrega una tarjeta con la información completa del deportista.
    """
    if not athlete_info:
        return
    
    commands.append(rect_command(x, y - height, width, height, fill=LIGHT_GRAY, stroke=TABLE_LINE))
    commands.append(text_command(x + 14, y - 22, "Información del deportista", 12, color=PRIMARY_COLOR, font="F2"))
    
    edad_str = str(athlete_info.get("EDAD", "")) if athlete_info.get("EDAD") is not None else ""
    
    fields = [
        ("Nombre", athlete_info.get("NOMBRE_DEPORTISTA", "")),
        ("Identificación", athlete_info.get("IDENTI_DEPORTISTA", "")),
        ("Edad", edad_str),
        ("Sexo", athlete_info.get("SEXO_DEPORTISTA", "")),
        ("Dirección", athlete_info.get("DIRECC_RESI", "")),
        ("Ciudad", athlete_info.get("CIUDAD_RESI", "")),
        ("Departamento", athlete_info.get("DEPARTA_RESI", "")),
        ("Correo", athlete_info.get("E_MAIL", "")),
        ("Teléfono", athlete_info.get("TELEFONO", "")),
        ("Entidad", athlete_info.get("ENTIDADES", "")),
        ("Deportes", athlete_info.get("DEPORTES", "")),
    ]
    
    row_y = y - 44
    for label, value in fields:
        if value:
            commands.append(text_command(x + 14, row_y, f"{label}:", 8, color=MUTED_COLOR))
            commands.append(text_command(x + 118, row_y, short_text(str(value), 42), 9, font="F2"))
            row_y -= 18


def build_longitudinal_pdf(records, athlete_info=None):
    ordered = sort_records_by_date(records)
    first = ordered[0] if ordered else None
    last = ordered[-1] if ordered else None
    athlete_name = display_value(record_value(last, "NOMBRE_DEPORTISTA")) if last else "---"
    identi = display_value(record_value(last, "IDENTI_DEPORTISTA")) if last else "---"
    period = f"{display_value(record_value(first, 'FECHA_MEDIDA'))} a {display_value(record_value(last, 'FECHA_MEDIDA'))}" if first and last else "---"

    page_one = []
    append_header(page_one, "Informe de análisis longitudinal", f"Deportista: {athlete_name} ({identi})")
    page_one.append(text_command(LEFT_MARGIN, 724, f"Periodo analizado: {period}", 10, color=LINE_COLOR, font="F2"))
    page_one.append(text_command(LEFT_MARGIN, 704, f"Total de valoraciones: {len(ordered)}", 9, color=MUTED_COLOR))
    
    # Agregar tarjeta de información del deportista si está disponible
    if athlete_info:
        append_athlete_info_card(page_one, athlete_info, LEFT_MARGIN, 672, 510, 180)
        append_longitudinal_summary_cards(page_one, ordered, LEFT_MARGIN, 472)
        append_longitudinal_table(page_one, ordered, LEFT_MARGIN, 364)
    else:
        append_longitudinal_summary_cards(page_one, ordered, LEFT_MARGIN, 672)
        append_longitudinal_table(page_one, ordered, LEFT_MARGIN, 564)
    
    page_one.append(text_command(LEFT_MARGIN, 82, "Lectura: el informe resume cambios entre la primera y última valoración disponible.", 8, color=MUTED_COLOR))

    page_two = []
    append_header(page_two, "Evolución de variables", f"Deportista: {athlete_name}")
    chart_specs = [
        ("Peso", "PESO_kg", "kg", LEFT_MARGIN, 716),
        ("IMC", "IMC", "", 320, 716),
        ("Grasa Yuhasz", "PorcRasoYuasz", "%", LEFT_MARGIN, 508),
        ("Masa muscular", "Mma", "kg", 320, 508),
        ("Endomorfismo", "Endomorfismo", "", LEFT_MARGIN, 300),
        ("Mesomorfismo", "Mesomorfismo", "", 320, 300),
    ]
    for label, field, unit, chart_x, chart_y in chart_specs:
        append_line_chart(page_two, label, build_pdf_metric_series(ordered, field), unit, chart_x, chart_y)

    page_three = []
    append_longitudinal_somatocarta(page_three, ordered)
    page_three.append(text_command(LEFT_MARGIN, 60, "Documento generado automáticamente por Somatocarta.", 8, color=MUTED_COLOR))

    streams = [
        "\n".join(page_one).encode("cp1252", errors="replace"),
        "\n".join(page_two).encode("cp1252", errors="replace"),
        "\n".join(page_three).encode("cp1252", errors="replace"),
    ]
    return build_pdf_document(streams, images=build_report_images())


def build_valoracion_pdf(record):
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    page_one = []
    append_header(page_one, "Resultados de valoración corporal", f"Generado: {generated_at}")
    append_info_card(page_one, record, LEFT_MARGIN, 724, 265, 126)
    append_metric_cards(page_one, record, 330, 724)
    append_table(page_one, "Mediciones antropométricas", MEASUREMENT_FIELDS, record, LEFT_MARGIN, 544, width=510, row_height=18)
    page_one.append(text_command(LEFT_MARGIN, 96, "Notas de lectura", 12, color=PRIMARY_COLOR, font="F2"))
    page_one.append(text_command(LEFT_MARGIN, 76, "Los cálculos provienen de la vista SQL CDRVistaValoracionCorporal.", 8, color=MUTED_COLOR))
    page_one.append(text_command(LEFT_MARGIN, 60, "Las unidades visibles corresponden a los datos antropométricos tomados en la valoración.", 8, color=MUTED_COLOR))

    page_two = []
    append_header(page_two, "Composición corporal", f"Deportista: {short_text(getattr(record, 'NOMBRE_DEPORTISTA', ''), 45)}")
    append_table(page_two, "Comparación de métodos de grasa y masas corporales", COMPOSITION_FIELDS, record, LEFT_MARGIN, 724, width=510, row_height=22)
    page_two.append(text_command(LEFT_MARGIN, 214, "Distribución corporal", 12, color=PRIMARY_COLOR, font="F2"))
    page_two.append(text_command(LEFT_MARGIN, 190, "Peso corporal:", 9, font="F2"))
    page_two.append(text_command(170, 190, value_with_unit(record, "PESO_kg", "kg"), 9))
    page_two.append(text_command(LEFT_MARGIN, 170, "Balance de masas:", 9, font="F2"))
    page_two.append(text_command(170, 170, "Masa grasa Johnston + masa muscular + masa ósea + masa residual.", 8, color=MUTED_COLOR))

    page_three = []
    append_analysis_page(page_three, record)

    page_four = []
    append_somatotype_page(page_four, record)

    page_five = []
    append_somatocarta_asset(page_five, record)
    page_five.append(text_command(LEFT_MARGIN, 48, "Documento generado automáticamente por Somatocarta.", 8, color=MUTED_COLOR))

    streams = [
        "\n".join(page_one).encode("cp1252", errors="replace"),
        "\n".join(page_two).encode("cp1252", errors="replace"),
        "\n".join(page_three).encode("cp1252", errors="replace"),
        "\n".join(page_four).encode("cp1252", errors="replace"),
        "\n".join(page_five).encode("cp1252", errors="replace"),
    ]
    return build_pdf_document(streams, images=build_report_images())
