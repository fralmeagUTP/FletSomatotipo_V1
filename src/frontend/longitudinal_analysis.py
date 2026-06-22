import math
from decimal import Decimal, InvalidOperation

import flet as ft

from src.frontend import theme
from src.frontend.assets import REFERENCE_IMAGES
from src.frontend.components import horizontal_scroll
from src.frontend.interpretation import longitudinal_reliability_message
from src.frontend.somatocarta import CHART_HEIGHT, CHART_WIDTH, coordinate_to_pixel


LONGITUDINAL_METRICS = [
    {"label": "Peso", "field": "PESO_kg", "unit": "kg", "semantic": "neutral"},
    {"label": "IMC", "field": "IMC", "unit": "", "semantic": "lower_better"},
    {"label": "Grasa Yuhasz", "field": "PorcRasoYuasz", "unit": "%", "semantic": "lower_better", "principal": True},
    {"label": "Grasa Faulkner", "field": "PorcGrasoFaulker", "unit": "%", "semantic": "lower_better"},
    {"label": "Masa grasa Yuhasz", "field": "PesoRasoYuazs", "unit": "kg", "semantic": "lower_better", "principal": True},
    {"label": "Masa grasa Faulkner", "field": "PesoRasoFaulker", "unit": "kg", "semantic": "lower_better"},
    {"label": "Masa muscular", "field": "Mma", "unit": "kg", "semantic": "higher_better"},
    {"label": "Endomorfismo", "field": "Endomorfismo", "unit": "", "semantic": "neutral"},
    {"label": "Mesomorfismo", "field": "Mesomorfismo", "unit": "", "semantic": "neutral"},
    {"label": "Ectomorfismo", "field": "Ectomorfismo", "unit": "", "semantic": "neutral"},
]

KPI_FIELDS = ["PESO_kg", "IMC", "PorcRasoYuasz", "PorcGrasoFaulker", "Mma"]


def parse_number(value):
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value).replace(",", ".")))
    except (InvalidOperation, ValueError):
        return None


def sort_rows_by_date(rows):
    return sorted(rows, key=lambda row: (str(row.get("FECHA_MEDIDA", "")), row.get("id_Somatotipo") or 0))


def format_value(value, unit=""):
    number = parse_number(value)
    if number is None:
        return "---"
    suffix = f" {unit}" if unit else ""
    return f"{number:.2f}{suffix}"


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


def metric_delta(series):
    if len(series) < 2:
        return None
    return series[-1]["value"] - series[0]["value"]


def trend_color(metric, delta):
    if delta is None or delta == 0:
        return theme.SUBTITLE_COLOR
    semantic = metric.get("semantic", "neutral")
    if semantic == "lower_better":
        return theme.SUCCESS_COLOR if delta < 0 else theme.ERROR_COLOR
    if semantic == "higher_better":
        return theme.SUCCESS_COLOR if delta > 0 else theme.ERROR_COLOR
    return theme.PRIMARY_COLOR if delta > 0 else theme.WARNING_COLOR


def trend_icon(delta):
    if delta is None or delta == 0:
        return ft.Icons.REMOVE
    return ft.Icons.ARROW_UPWARD if delta > 0 else ft.Icons.ARROW_DOWNWARD


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
    delta = metric_delta(series)
    if delta is None:
        return "Sin tendencia"
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


def metric_by_field(field):
    return next(metric for metric in LONGITUDINAL_METRICS if metric["field"] == field)


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


def build_trajectory_segment(start, end, color):
    start_x, start_y = coordinate_to_pixel(start["x"], start["y"])
    end_x, end_y = coordinate_to_pixel(end["x"], end["y"])
    delta_x = end_x - start_x
    delta_y = end_y - start_y
    length = math.hypot(delta_x, delta_y)
    if length < 1:
        return None
    angle = math.atan2(delta_y, delta_x)
    return ft.Container(
        left=start_x,
        top=start_y - 1,
        width=length,
        height=2,
        bgcolor=color,
        opacity=0.55,
        rotate=ft.Rotate(angle=angle, alignment=ft.alignment.center_left),
    )


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
            src=REFERENCE_IMAGES["somatocarta"],
            width=CHART_WIDTH,
            height=CHART_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("No se pudo cargar la somatocarta.", color=theme.ERROR_COLOR),
        )
    ]
    for start, end in zip(points, points[1:]):
        segment = build_trajectory_segment(start, end, theme.PRIMARY_COLOR)
        if segment:
            controls.append(segment)

    legend_rows = []
    for point_index, point in enumerate(points):
        point_x, point_y = coordinate_to_pixel(point["x"], point["y"])
        color = palette[point_index % len(palette)]
        date_label = point["date"] or f"Valoración {point['index']}"
        is_latest = point_index == len(points) - 1
        controls.append(
            ft.Container(
                left=point_x - (9 if is_latest else 7),
                top=point_y - (9 if is_latest else 7),
                width=18 if is_latest else 14,
                height=18 if is_latest else 14,
                bgcolor=color,
                border=ft.border.all(3 if is_latest else 2, ft.Colors.WHITE),
                border_radius=18,
                shadow=ft.BoxShadow(blur_radius=8, color="#55000000"),
                tooltip=f"{date_label}: X={point['x']:.2f} · Y={point['y']:.2f}",
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
                            color=theme.TEXT_COLOR if is_latest else theme.SUBTITLE_COLOR,
                            weight=ft.FontWeight.BOLD if is_latest else None,
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
                    "La línea muestra el recorrido cronológico; el último punto queda resaltado.",
                    size=12,
                    color=theme.SUBTITLE_COLOR,
                ),
                horizontal_scroll(chart),
                ft.Container(
                    content=ft.Column(legend_rows, spacing=0, scroll=ft.ScrollMode.AUTO),
                    height=110,
                    padding=10,
                    bgcolor=theme.SURFACE_MUTED,
                    border_radius=8,
                ),
            ],
            spacing=8,
        ),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=10,
        width=float("inf"),
    )


def chart_axis_labels(series):
    return [
        ft.ChartAxisLabel(
            value=point["index"],
            label=ft.Text(compact_date_label(point["date"]), size=10, color=theme.SUBTITLE_COLOR),
        )
        for point in series
    ]


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

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                points=chart_points,
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
        bottom_axis=ft.ChartAxis(show_labels=True, labels=chart_axis_labels(series), label_size=34),
        left_axis=ft.ChartAxis(show_labels=True, label_size=42),
        interactive=True,
        width=620,
        height=260,
    )
    return ft.Container(
        content=horizontal_scroll(chart),
        height=280,
        padding=8,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        width=float("inf"),
    )


def build_combined_chart(rows):
    weight_metric = metric_by_field("PESO_kg")
    muscle_metric = metric_by_field("Mma")
    weight_series = build_metric_series(rows, weight_metric["field"])
    muscle_series = build_metric_series(rows, muscle_metric["field"])
    if len(weight_series) < 2 or len(muscle_series) < 2:
        return ft.Container(
            content=ft.Text(
                "No hay datos suficientes para comparar peso y masa muscular.",
                color=theme.SUBTITLE_COLOR,
            ),
            padding=18,
            bgcolor=theme.SURFACE_MUTED,
            border_radius=8,
        )

    all_values = [point["value"] for point in weight_series + muscle_series]
    min_value = min(all_values)
    max_value = max(all_values)
    padding = max((max_value - min_value) * 0.15, 1)

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                points=[
                    ft.LineChartDataPoint(point["index"], point["value"], tooltip=f"Peso {point['date']}: {point['value']:.2f} kg")
                    for point in weight_series
                ],
                color=theme.PRIMARY_COLOR,
                stroke_width=3,
                point=ft.ChartCirclePoint(color=theme.PRIMARY_COLOR, radius=4),
            ),
            ft.LineChartData(
                points=[
                    ft.LineChartDataPoint(point["index"], point["value"], tooltip=f"Masa {point['date']}: {point['value']:.2f} kg")
                    for point in muscle_series
                ],
                color=theme.SUCCESS_COLOR,
                stroke_width=3,
                point=ft.ChartCirclePoint(color=theme.SUCCESS_COLOR, radius=4),
            ),
        ],
        min_x=1,
        max_x=max(point["index"] for point in weight_series),
        min_y=min_value - padding,
        max_y=max_value + padding,
        horizontal_grid_lines=ft.ChartGridLines(interval=padding, color="#e1e7f0", width=1),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color="#edf1f7", width=1),
        bottom_axis=ft.ChartAxis(show_labels=True, labels=chart_axis_labels(weight_series), label_size=34),
        left_axis=ft.ChartAxis(show_labels=True, label_size=42),
        interactive=True,
        width=620,
        height=250,
    )
    legend = ft.Row(
        [
            ft.Row([ft.Container(width=10, height=10, bgcolor=theme.PRIMARY_COLOR, border_radius=10), ft.Text("Peso", size=11)]),
            ft.Row([ft.Container(width=10, height=10, bgcolor=theme.SUCCESS_COLOR, border_radius=10), ft.Text("Masa muscular", size=11)]),
        ],
        spacing=18,
        wrap=True,
    )
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Comparación peso vs masa muscular", size=14, weight="bold", color=theme.TEXT_COLOR),
                legend,
                horizontal_scroll(chart),
            ],
            spacing=8,
        ),
        padding=8,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        width=float("inf"),
    )


def build_fat_method_chart(rows):
    faulkner_metric = metric_by_field("PorcGrasoFaulker")
    yuhasz_metric = metric_by_field("PorcRasoYuasz")
    faulkner_series = build_metric_series(rows, faulkner_metric["field"])
    yuhasz_series = build_metric_series(rows, yuhasz_metric["field"])
    if len(faulkner_series) < 2 or len(yuhasz_series) < 2:
        return ft.Container(
            content=ft.Text(
                "No hay datos suficientes para comparar Yuhasz y Faulkner.",
                color=theme.SUBTITLE_COLOR,
            ),
            padding=18,
            bgcolor=theme.SURFACE_MUTED,
            border_radius=8,
        )

    all_values = [point["value"] for point in faulkner_series + yuhasz_series]
    min_value = min(all_values)
    max_value = max(all_values)
    padding = max((max_value - min_value) * 0.15, 1)

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                points=[
                    ft.LineChartDataPoint(
                        point["index"],
                        point["value"],
                        tooltip=f"Faulkner {point['date']}: {point['value']:.2f} %",
                    )
                    for point in faulkner_series
                ],
                color=theme.WARNING_COLOR,
                stroke_width=3,
                point=ft.ChartCirclePoint(
                    color=theme.WARNING_COLOR,
                    radius=4,
                    stroke_color=ft.Colors.WHITE,
                    stroke_width=2,
                ),
            ),
            ft.LineChartData(
                points=[
                    ft.LineChartDataPoint(
                        point["index"],
                        point["value"],
                        tooltip=f"Yuhasz {point['date']}: {point['value']:.2f} %",
                    )
                    for point in yuhasz_series
                ],
                color=theme.PRIMARY_COLOR,
                stroke_width=4,
                point=ft.ChartCirclePoint(
                    color=theme.PRIMARY_COLOR,
                    radius=5,
                    stroke_color=ft.Colors.WHITE,
                    stroke_width=2,
                ),
            ),
        ],
        min_x=1,
        max_x=max(point["index"] for point in yuhasz_series),
        min_y=min_value - padding,
        max_y=max_value + padding,
        horizontal_grid_lines=ft.ChartGridLines(interval=padding, color="#e1e7f0", width=1),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color="#edf1f7", width=1),
        bottom_axis=ft.ChartAxis(show_labels=True, labels=chart_axis_labels(yuhasz_series), label_size=34),
        left_axis=ft.ChartAxis(show_labels=True, label_size=42),
        interactive=True,
        width=620,
        height=250,
    )
    legend = ft.Row(
        [
            ft.Row(
                [
                    ft.Container(width=10, height=10, bgcolor=theme.PRIMARY_COLOR, border_radius=10),
                    ft.Text("Yuhasz principal", size=11, weight=ft.FontWeight.BOLD),
                ]
            ),
            ft.Row(
                [
                    ft.Container(width=10, height=10, bgcolor=theme.WARNING_COLOR, border_radius=10),
                    ft.Text("Faulkner", size=11),
                ]
            ),
        ],
        spacing=18,
        wrap=True,
    )
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Análisis de grasa: Yuhasz vs Faulkner", size=14, weight="bold", color=theme.TEXT_COLOR),
                ft.Text("Yuhasz se muestra como método principal para población deportiva.", size=12, color=theme.SUBTITLE_COLOR),
                legend,
                horizontal_scroll(chart),
            ],
            spacing=8,
        ),
        padding=8,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        width=float("inf"),
    )


def build_metric_cards(rows):
    latest = sort_rows_by_date(rows)[-1] if rows else {}
    cards = []
    for field in KPI_FIELDS:
        metric = metric_by_field(field)
        value = latest.get(metric["field"])
        series = build_metric_series(rows, metric["field"])
        delta = metric_delta(series)
        color = trend_color(metric, delta)
        cards.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(metric["label"], size=12, color=theme.SUBTITLE_COLOR),
                        ft.Text(format_value(value, metric["unit"]), size=18, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                        ft.Row(
                            [
                                ft.Icon(trend_icon(delta), size=14, color=color),
                                ft.Text(delta_text(series, metric["unit"]), size=11, color=color, weight=ft.FontWeight.BOLD),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=4,
                ),
                bgcolor=theme.SURFACE_MUTED,
                padding=12,
                border_radius=8,
                col={"xs": 6, "sm": 4, "md": 3},
            )
        )
    return ft.ResponsiveRow(cards, spacing=10, run_spacing=10)


def build_selected_metric_cards(series, metric):
    delta = metric_delta(series)
    color = trend_color(metric, delta)
    first = "---" if not series else f"{series[0]['value']:.2f} {metric['unit']}".strip()
    last = "---" if not series else f"{series[-1]['value']:.2f} {metric['unit']}".strip()
    cards = [
        ("Valor inicial", first, theme.TEXT_COLOR),
        ("Valor final", last, theme.TEXT_COLOR),
        ("Cambio absoluto", delta_text(series, metric["unit"]), color),
        ("Cambio porcentual", percent_change_text(series), color),
    ]
    return ft.ResponsiveRow(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(label, size=12, color=theme.SUBTITLE_COLOR),
                        ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color=value_color),
                    ],
                    spacing=3,
                ),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, theme.SURFACE_BORDER),
                padding=12,
                border_radius=8,
                col={"xs": 6, "sm": 6, "md": 3},
            )
            for label, value, value_color in cards
        ],
        spacing=10,
        run_spacing=10,
    )


def build_historical_table(rows):
    ordered = sort_rows_by_date(rows)
    columns = [
        "Fecha",
        "Peso",
        "IMC",
        "Grasa Yuhasz",
        "Grasa Faulkner",
        "Masa grasa Yuhasz",
        "Masa muscular",
        "X",
        "Y",
    ]
    table_rows = []
    for index, row in enumerate(ordered):
        bgcolor = "#f8fafc" if index % 2 else ft.Colors.WHITE
        table_rows.append(
            ft.DataRow(
                color=bgcolor,
                cells=[
                    ft.DataCell(ft.Text(str(row.get("FECHA_MEDIDA", "")), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("PESO_kg"), "kg"), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("IMC")), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("PorcRasoYuasz"), "%"), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("PorcGrasoFaulker"), "%"), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("PesoRasoYuazs"), "kg"), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("Mma"), "kg"), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("X")), size=12)),
                    ft.DataCell(ft.Text(format_value(row.get("Y")), size=12)),
                ],
            )
        )

    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(column, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR)) for column in columns],
        rows=table_rows,
        heading_row_color=theme.SURFACE_MUTED,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        horizontal_lines=ft.BorderSide(1, theme.SURFACE_BORDER),
    )
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Histórico de valoraciones", size=16, weight="bold", color=theme.PRIMARY_COLOR),
                ft.Text("Tabla separada para revisar datos base y comparar registros.", size=12, color=theme.SUBTITLE_COLOR),
                horizontal_scroll(table),
            ],
            spacing=8,
        ),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=10,
        width=float("inf"),
    )


def build_longitudinal_panel(rows):
    selected_metric = metric_by_field("PorcRasoYuasz")
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
        metric = next(item for item in LONGITUDINAL_METRICS if item["field"] == event.control.value)
        render_metric(metric)
        event.page.update()

    metric_dropdown.on_change = change_metric
    render_metric(selected_metric)

    trend_panel = ft.Container(
        content=ft.Column(
            [
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
                selected_metric_container,
                chart_container,
                build_fat_method_chart(rows),
                build_longitudinal_somatocarta(rows),
                build_combined_chart(rows),
                summary_text,
            ],
            spacing=12,
        ),
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=10,
        width=float("inf"),
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Resumen longitudinal", size=20, weight="bold", color=theme.PRIMARY_COLOR),
                ft.Text(period_summary(rows), color=theme.SUBTITLE_COLOR, size=13),
                build_metric_cards(rows),
                trend_panel,
                build_historical_table(rows),
                reliability_text,
            ],
            spacing=12,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=16,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        width=float("inf"),
    )
