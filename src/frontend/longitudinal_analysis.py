from decimal import Decimal, InvalidOperation

import flet as ft

from src.frontend import theme
from src.frontend.components import horizontal_scroll
from src.frontend.assets import REFERENCE_IMAGES, asset_path
from src.frontend.interpretation import longitudinal_reliability_message
from src.frontend.somatocarta import CHART_HEIGHT, CHART_WIDTH, coordinate_to_pixel


LONGITUDINAL_METRICS = [
    {"label": "Peso", "field": "PESO_kg", "unit": "kg"},
    {"label": "IMC", "field": "IMC", "unit": ""},
    {"label": "Porcentaje graso Yuhasz", "field": "PorcRasoYuasz", "unit": "%"},
    {"label": "Porcentaje graso Faulkner", "field": "PorcGrasoFaulker", "unit": "%"},
    {"label": "Masa muscular", "field": "Mma", "unit": "kg"},
    {"label": "Endomorfismo", "field": "Endomorfismo", "unit": ""},
    {"label": "Mesomorfismo", "field": "Mesomorfismo", "unit": ""},
    {"label": "Ectomorfismo", "field": "Ectomorfismo", "unit": ""},
]


def parse_number(value):
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value).replace(",", ".")))
    except (InvalidOperation, ValueError):
        return None


def sort_rows_by_date(rows):
    return sorted(rows, key=lambda row: (str(row.get("FECHA_MEDIDA", "")), row.get("id_Somatotipo") or 0))


def build_metric_series(rows, field):
    series = []
    for index, row in enumerate(sort_rows_by_date(rows), start=1):
        value = parse_number(row.get(field))
        if value is not None:
            series.append(
                {
                    "index": index,
                    "value": value,
                    "date": str(row.get("FECHA_MEDIDA", "")),
                    "id": row.get("id_Somatotipo"),
                }
            )
    return series


def trend_summary(series, unit=""):
    if len(series) < 2:
        return "Se requieren al menos dos valoraciones para analizar tendencia."
    first = series[0]["value"]
    last = series[-1]["value"]
    delta = last - first
    direction = "subió" if delta > 0 else "bajó" if delta < 0 else "se mantuvo"
    suffix = f" {unit}" if unit else ""
    start_date = series[0].get("date", "")
    end_date = series[-1].get("date", "")
    return f"{len(series)} valoraciones: de {start_date} a {end_date}, {direction} {abs(delta):.2f}{suffix}."


def period_summary(rows):
    ordered = sort_rows_by_date(rows)
    if not ordered:
        return "Sin valoraciones registradas."
    start_date = ordered[0].get("FECHA_MEDIDA", "")
    end_date = ordered[-1].get("FECHA_MEDIDA", "")
    if start_date == end_date:
        return f"{len(ordered)} valoración(es) registradas el {start_date}."
    return f"{len(ordered)} valoración(es) entre {start_date} y {end_date}."


def delta_text(series, unit=""):
    if len(series) < 2:
        return "Sin tendencia"
    delta = series[-1]["value"] - series[0]["value"]
    sign = "+" if delta > 0 else ""
    suffix = f" {unit}" if unit else ""
    return f"{sign}{delta:.2f}{suffix}"


def percent_change_text(series):
    if len(series) < 2:
        return "Sin cambio porcentual"
    first = series[0]["value"]
    if first == 0:
        return "Cambio porcentual no calculable"
    delta = series[-1]["value"] - first
    sign = "+" if delta > 0 else ""
    return f"{sign}{((delta / first) * 100):.2f} %"


def compact_date_label(value):
    text = str(value or "")
    if len(text) >= 10:
        return text[5:10]
    return text


def build_somatocarta_points(rows):
    points = []
    for index, row in enumerate(sort_rows_by_date(rows), start=1):
        x_value = parse_number(row.get("X"))
        y_value = parse_number(row.get("Y"))
        if x_value is None or y_value is None:
            continue
        points.append(
            {
                "index": index,
                "x": x_value,
                "y": y_value,
                "date": str(row.get("FECHA_MEDIDA", "")),
                "id": row.get("id_Somatotipo"),
            }
        )
    return points


def build_longitudinal_somatocarta(rows):
    points = build_somatocarta_points(rows)
    if not points:
        return ft.Container(
            content=ft.Text(
                "No hay valoraciones con coordenadas X/Y para mostrar en la somatocarta.",
                color=theme.SUBTITLE_COLOR,
            ),
            padding=20,
            bgcolor=theme.SURFACE_MUTED,
            border_radius=8,
        )

    palette = [
        "#ff3b30",
        "#2e5cb8",
        "#00a86b",
        "#f59e0b",
        "#8b5cf6",
        "#0891b2",
        "#db2777",
        "#64748b",
    ]
    controls = [
        ft.Image(
            src=asset_path(REFERENCE_IMAGES["somatocarta"]),
            width=CHART_WIDTH,
            height=CHART_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
        )
    ]
    legend_rows = []
    for point_index, point in enumerate(points):
        point_x, point_y = coordinate_to_pixel(point["x"], point["y"])
        color = palette[point_index % len(palette)]
        date_label = point["date"] or f"Valoración {point['index']}"
        controls.append(
            ft.Container(
                left=point_x - 7,
                top=point_y - 7,
                width=14,
                height=14,
                bgcolor=color,
                border=ft.border.all(2, ft.Colors.WHITE),
                border_radius=14,
                shadow=ft.BoxShadow(blur_radius=6, color="#55000000"),
            )
        )
        legend_rows.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(width=10, height=10, bgcolor=color, border_radius=10),
                        ft.Text(
                            f"{date_label}: X={point['x']:.2f} · Y={point['y']:.2f}",
                            size=11,
                            color=theme.SUBTITLE_COLOR,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=2),
            )
        )

    chart = ft.Stack(controls=controls, width=CHART_WIDTH, height=CHART_HEIGHT)
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Somatocarta longitudinal", size=16, weight="bold", color=theme.PRIMARY_COLOR),
                ft.Text(
                    "Cada punto representa una valoración y muestra la fecha de medición.",
                    size=12,
                    color=theme.SUBTITLE_COLOR,
                ),
                horizontal_scroll(chart),
                ft.Container(
                    content=ft.Column(legend_rows, spacing=0),
                    padding=10,
                    bgcolor=theme.SURFACE_MUTED,
                    border_radius=8,
                ),
            ],
            spacing=8,
        ),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, "#eeeeee"),
        border_radius=10,
    )


def build_longitudinal_chart(rows, metric):
    series = build_metric_series(rows, metric["field"])
    if len(series) < 2:
        return ft.Container(
            content=ft.Text(
                "No hay suficientes valoraciones con datos numéricos para graficar esta variable.",
                color=theme.SUBTITLE_COLOR,
            ),
            padding=20,
            bgcolor=theme.SURFACE_MUTED,
            border_radius=8,
        )

    values = [point["value"] for point in series]
    min_value = min(values)
    max_value = max(values)
    padding = max((max_value - min_value) * 0.15, 1)

    chart_points = [
        ft.LineChartDataPoint(
            point["index"],
            point["value"],
            tooltip=f"{point['date']}: {point['value']:.2f} {metric['unit']}".strip(),
            show_tooltip=point == series[-1],
        )
        for point in series
    ]
    axis_labels = [
        ft.ChartAxisLabel(
            value=point["index"],
            label=ft.Text(compact_date_label(point["date"]), size=10, color=theme.SUBTITLE_COLOR),
        )
        for point in series
    ]

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=chart_points,
                color=theme.PRIMARY_COLOR,
                stroke_width=3,
                point=ft.ChartCirclePoint(
                    color=theme.PRIMARY_COLOR,
                    radius=5,
                    stroke_color=ft.Colors.WHITE,
                    stroke_width=2,
                ),
            )
        ],
        min_x=1,
        max_x=max(point["index"] for point in series),
        min_y=min_value - padding,
        max_y=max_value + padding,
        horizontal_grid_lines=ft.ChartGridLines(interval=padding, color="#e1e7f0", width=1),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color="#edf1f7", width=1),
        bottom_axis=ft.ChartAxis(show_labels=True, labels=axis_labels, labels_size=34),
        left_axis=ft.ChartAxis(show_labels=True, labels_size=36),
        tooltip_bgcolor=theme.TEXT_COLOR,
        tooltip_rounded_radius=6,
        interactive=True,
        width=560,
        height=260,
    )
    return ft.Container(content=horizontal_scroll(chart), height=280, padding=8, bgcolor=ft.Colors.WHITE, border_radius=8)


def build_metric_cards(rows):
    latest = sort_rows_by_date(rows)[-1] if rows else {}
    cards = []
    for metric in LONGITUDINAL_METRICS[:4]:
        value = latest.get(metric["field"])
        text = "---" if value is None else f"{value} {metric['unit']}".strip()
        series = build_metric_series(rows, metric["field"])
        cards.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(metric["label"], size=12, color=theme.SUBTITLE_COLOR),
                        ft.Text(str(text), size=18, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                        ft.Text(f"Cambio: {delta_text(series, metric['unit'])}", size=11, color=theme.SUBTITLE_COLOR),
                    ],
                    spacing=3,
                ),
                bgcolor=theme.SURFACE_MUTED,
                padding=12,
                border_radius=8,
                col={"xs": 12, "sm": 6, "md": 3},
            )
        )
    return ft.ResponsiveRow(cards, spacing=10, run_spacing=10)


def build_selected_metric_cards(series, metric):
    first = "---" if not series else f"{series[0]['value']:.2f} {metric['unit']}".strip()
    last = "---" if not series else f"{series[-1]['value']:.2f} {metric['unit']}".strip()
    cards = [
        ("Valor inicial", first),
        ("Valor final", last),
        ("Cambio absoluto", delta_text(series, metric["unit"])),
        ("Cambio porcentual", percent_change_text(series)),
    ]
    return ft.ResponsiveRow(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(label, size=12, color=theme.SUBTITLE_COLOR),
                        ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                    ],
                    spacing=3,
                ),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, "#eeeeee"),
                padding=12,
                border_radius=8,
                col={"xs": 12, "sm": 6, "md": 3},
            )
            for label, value in cards
        ],
        spacing=10,
        run_spacing=10,
    )


def build_longitudinal_panel(rows):
    selected_metric = LONGITUDINAL_METRICS[0]
    chart_container = ft.Container()
    selected_metric_container = ft.Container()
    summary_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    reliability_text = ft.Text(
        longitudinal_reliability_message(len(rows)),
        color=theme.SUBTITLE_COLOR,
        size=12,
    )

    def render_metric(metric):
        series = build_metric_series(rows, metric["field"])
        selected_metric_container.content = build_selected_metric_cards(series, metric)
        chart_container.content = build_longitudinal_chart(rows, metric)
        summary_text.value = trend_summary(series, metric["unit"])

    metric_dropdown = ft.Dropdown(
        label="Variable a graficar",
        value=selected_metric["field"],
        options=[ft.dropdown.Option(metric["field"], metric["label"]) for metric in LONGITUDINAL_METRICS],
        width=280,
    )

    def change_metric(event):
        metric = next(
            item for item in LONGITUDINAL_METRICS if item["field"] == event.control.value
        )
        render_metric(metric)
        event.page.update()

    metric_dropdown.on_change = change_metric
    render_metric(selected_metric)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Análisis longitudinal", size=20, weight="bold", color=theme.PRIMARY_COLOR),
                ft.Text(
                    period_summary(rows),
                    color=theme.SUBTITLE_COLOR,
                    size=13,
                ),
                build_metric_cards(rows),
                selected_metric_container,
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Selecciona una variable para revisar su evolución temporal.",
                                color=theme.SUBTITLE_COLOR,
                                size=12,
                            ),
                            col={"xs": 12, "md": 7},
                            alignment=ft.alignment.center_left,
                        ),
                        ft.Container(
                            content=metric_dropdown,
                            col={"xs": 12, "md": 5},
                            alignment=ft.alignment.center_right,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                chart_container,
                build_longitudinal_somatocarta(rows),
                summary_text,
                reliability_text,
            ],
            spacing=12,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=16,
        border=ft.border.all(1, "#eeeeee"),
    )
