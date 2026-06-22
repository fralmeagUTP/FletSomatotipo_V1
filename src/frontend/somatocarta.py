from decimal import Decimal, InvalidOperation

import flet as ft

from src.frontend import theme
from src.frontend.assets import REFERENCE_IMAGES
from src.frontend.components import horizontal_scroll


X_MIN = -8
X_MAX = 8
Y_MIN = -10
Y_MAX = 16

SOURCE_WIDTH = 1122
SOURCE_HEIGHT = 1402
SOURCE_X_AXIS_LEFT = 132
SOURCE_X_AXIS_RIGHT = 923
SOURCE_Y_AXIS_TOP = 346
SOURCE_Y_AXIS_BOTTOM = 1190
SOURCE_X_TICKS = [
    (-8, 131.5),
    (-7, 182.0),
    (-6, 233.5),
    (-5, 284.5),
    (-4, 336.0),
    (-3, 388.5),
    (-2, 439.5),
    (-1, 490.5),
    (0, 543.5),
    (1, 593.5),
    (2, 644.5),
    (3, 694.5),
    (4, 743.5),
    (5, 791.5),
    (6, 839.5),
    (7, 885.5),
    (8, 927.5),
]
SOURCE_Y_TICKS = [
    (16, 348.5),
    (14, 413.5),
    (12, 477.5),
    (10, 547.0),
    (8, 613.5),
    (6, 680.0),
    (4, 747.5),
    (2, 812.5),
    (0, 876.5),
    (-2, 944.0),
    (-4, 1009.0),
    (-6, 1073.5),
    (-8, 1136.0),
    (-10, 1190.0),
]

CHART_WIDTH = 760
CHART_HEIGHT = round(CHART_WIDTH * (SOURCE_HEIGHT / SOURCE_WIDTH))
SCALE = CHART_WIDTH / SOURCE_WIDTH


def parse_coordinate(value):
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value).replace(",", ".")))
    except (InvalidOperation, ValueError):
        return None


def clamp_coordinate(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def interpolate_tick_position(value, ticks):
    sorted_ticks = sorted(ticks, key=lambda tick: tick[0])
    if value <= sorted_ticks[0][0]:
        return sorted_ticks[0][1]
    if value >= sorted_ticks[-1][0]:
        return sorted_ticks[-1][1]

    for (lower_value, lower_position), (upper_value, upper_position) in zip(sorted_ticks, sorted_ticks[1:]):
        if lower_value <= value <= upper_value:
            ratio = (value - lower_value) / (upper_value - lower_value)
            return lower_position + ratio * (upper_position - lower_position)

    return sorted_ticks[-1][1]


def coordinate_to_pixel(x_value: float, y_value: float):
    clamped_x = clamp_coordinate(x_value, X_MIN, X_MAX)
    clamped_y = clamp_coordinate(y_value, Y_MIN, Y_MAX)
    source_x = interpolate_tick_position(clamped_x, SOURCE_X_TICKS)
    source_y = interpolate_tick_position(clamped_y, SOURCE_Y_TICKS)
    return round(source_x * SCALE, 2), round(source_y * SCALE, 2)


def build_athlete_marker(point_x, point_y, label):
    athlete_label = label or "Deportista"
    return [
        ft.Container(
            left=point_x - 9,
            top=point_y - 9,
            width=18,
            height=18,
            bgcolor="#ff3b30",
            border=ft.border.all(3, ft.Colors.WHITE),
            border_radius=18,
            shadow=ft.BoxShadow(blur_radius=8, color="#66000000"),
        ),
        ft.Container(
            left=min(point_x + 12, CHART_WIDTH - 205),
            top=max(point_y - 15, 8),
            content=ft.Text(athlete_label, size=12, color="#0b2f6b", weight="bold"),
            bgcolor="#ffffffcc",
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        ),
    ]


def build_coordinate_badge(x_coord, y_coord):
    return ft.Container(
        left=24,
        top=CHART_HEIGHT - 58,
        content=ft.Row(
            [
                ft.Icon(ft.Icons.MY_LOCATION, size=16, color=theme.PRIMARY_COLOR),
                ft.Text(f"Deportista: X={x_coord:.2f} · Y={y_coord:.2f}", size=12, color=theme.TEXT_COLOR),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#ffffffdd",
        border=ft.border.all(1, "#dbe5f5"),
        border_radius=18,
        padding=ft.padding.symmetric(horizontal=12, vertical=7),
    )


def build_somatocarta_chart(x_value, y_value, label: str = ""):
    x_coord = parse_coordinate(x_value)
    y_coord = parse_coordinate(y_value)
    if x_coord is None or y_coord is None:
        return None

    point_x, point_y = coordinate_to_pixel(x_coord, y_coord)
    controls = [
        ft.Image(
            src=REFERENCE_IMAGES["somatocarta"],
            width=CHART_WIDTH,
            height=CHART_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("No se pudo cargar la somatocarta.", color=theme.ERROR_COLOR),
        ),
        build_coordinate_badge(x_coord, y_coord),
    ]
    controls.extend(build_athlete_marker(point_x, point_y, label))
    return ft.Stack(controls=controls, width=CHART_WIDTH, height=CHART_HEIGHT)


def build_somatocarta_card(x_value, y_value, label: str = ""):
    chart = build_somatocarta_chart(x_value, y_value, label)
    if chart is None:
        body = ft.Text("No hay coordenadas X/Y disponibles para graficar.", color=theme.SUBTITLE_COLOR)
    else:
        body = ft.Container(
            content=horizontal_scroll(chart),
            alignment=ft.alignment.center,
            expand=True,
        )

    subtitle = f"{label} · " if label else ""
    x_coord = parse_coordinate(x_value)
    y_coord = parse_coordinate(y_value)
    coordinates = "sin coordenadas" if chart is None else f"X={x_coord:.2f} · Y={y_coord:.2f}"

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Somatocarta", size=16, weight="bold", color=theme.PRIMARY_COLOR),
                ft.Text(f"{subtitle}{coordinates}", size=12, color=theme.SUBTITLE_COLOR),
                body,
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, "#e3e8f0"),
        border_radius=14,
        padding=12,
    )
