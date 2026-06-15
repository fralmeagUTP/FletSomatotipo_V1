import flet as ft

from src.frontend import theme
from src.frontend.components import horizontal_scroll
from src.frontend.interpretation import fat_equation_warning, parse_float


MASS_BALANCE_THRESHOLD_PERCENT = 5.0
MASS_COLORS = [
    ft.Colors.ORANGE_400,
    ft.Colors.BLUE_400,
    ft.Colors.GREEN_400,
    ft.Colors.PURPLE_300,
]


def format_number(value, decimals=2):
    number = parse_float(value)
    if number is None:
        return "---"
    return f"{number:.{decimals}f}"


def percent_of_weight(value, body_weight):
    numeric_value = parse_float(value)
    numeric_weight = parse_float(body_weight)
    if numeric_value is None or numeric_weight in (None, 0):
        return None
    return (numeric_value / numeric_weight) * 100


def build_composition_rows(detail):
    return [
        {
            "component": "Grasa corporal",
            "value": detail.get("PorcGrasoJonson"),
            "unit": "%",
            "method": "Johnston",
            "kind": "percent",
        },
        {
            "component": "Grasa corporal",
            "value": detail.get("PorcGrasoFaulker"),
            "unit": "%",
            "method": "Faulkner",
            "kind": "percent",
        },
        {
            "component": "Grasa corporal",
            "value": detail.get("PorcRasoYuasz"),
            "unit": "%",
            "method": "Yuhasz",
            "kind": "percent",
        },
        {
            "component": "Masa grasa",
            "value": detail.get("PesoGrasoJhonston"),
            "unit": "kg",
            "method": "Johnston",
            "kind": "mass",
        },
        {
            "component": "Masa grasa",
            "value": detail.get("PesoRasoFaulker"),
            "unit": "kg",
            "method": "Faulkner",
            "kind": "mass",
        },
        {
            "component": "Masa grasa",
            "value": detail.get("PesoRasoYuazs"),
            "unit": "kg",
            "method": "Yuhasz",
            "kind": "mass",
        },
    ]


def build_fat_method_rows(detail):
    body_weight = detail.get("PESO_kg")
    return [
        {
            "method": "Johnston",
            "fat_percent": parse_float(detail.get("PorcGrasoJonson")),
            "fat_mass": parse_float(detail.get("PesoGrasoJhonston")),
            "percent_of_weight": percent_of_weight(detail.get("PesoGrasoJhonston"), body_weight),
            "use": "Método principal",
        },
        {
            "method": "Faulkner",
            "fat_percent": parse_float(detail.get("PorcGrasoFaulker")),
            "fat_mass": parse_float(detail.get("PesoRasoFaulker")),
            "percent_of_weight": percent_of_weight(detail.get("PesoRasoFaulker"), body_weight),
            "use": "Referencia comparativa",
        },
        {
            "method": "Yuhasz",
            "fat_percent": parse_float(detail.get("PorcRasoYuasz")),
            "fat_mass": parse_float(detail.get("PesoRasoYuazs")),
            "percent_of_weight": percent_of_weight(detail.get("PesoRasoYuazs"), body_weight),
            "use": "Referencia comparativa",
        },
    ]


def build_mass_distribution_rows(detail):
    body_weight = parse_float(detail.get("PESO_kg"))
    rows = [
        {"component": "Masa grasa Johnston", "value": parse_float(detail.get("PesoGrasoJhonston")), "role": "Grasa"},
        {"component": "Masa muscular", "value": parse_float(detail.get("Mma")), "role": "Magra"},
        {"component": "Masa ósea", "value": parse_float(detail.get("PesoOseo")), "role": "Estructural"},
        {"component": "Masa residual", "value": parse_float(detail.get("PesoResidual")), "role": "Residual"},
    ]
    component_total = sum(row["value"] for row in rows if row["value"] is not None)
    difference = None if body_weight is None else body_weight - component_total

    for row in rows:
        row["percent"] = percent_of_weight(row["value"], body_weight)
        row["is_total"] = False

    total_rows = [
        {
            "component": "Peso corporal",
            "value": body_weight,
            "percent": 100.0 if body_weight else None,
            "role": "Medición directa",
            "is_total": True,
        },
        {
            "component": "Suma calculada",
            "value": component_total,
            "percent": percent_of_weight(component_total, body_weight),
            "role": "Suma de masas",
            "is_total": True,
        },
        {
            "component": "Diferencia",
            "value": difference,
            "percent": percent_of_weight(difference, body_weight),
            "role": "Peso - suma",
            "is_total": True,
        },
    ]
    return total_rows[:1] + rows + total_rows[1:]


def mass_balance_summary(detail, threshold_percent=MASS_BALANCE_THRESHOLD_PERCENT):
    body_weight = parse_float(detail.get("PESO_kg"))
    components = [
        parse_float(detail.get("PesoGrasoJhonston")),
        parse_float(detail.get("Mma")),
        parse_float(detail.get("PesoOseo")),
        parse_float(detail.get("PesoResidual")),
    ]
    if body_weight is None or any(value is None for value in components):
        return None

    component_total = sum(components)
    difference = abs(body_weight - component_total)
    threshold_kg = body_weight * (threshold_percent / 100)
    return {
        "body_weight": body_weight,
        "component_total": component_total,
        "difference": difference,
        "threshold_kg": threshold_kg,
        "is_warning": difference > threshold_kg,
    }


def mass_balance_message(summary):
    if not summary:
        return None
    base = (
        f"Peso corporal: {summary['body_weight']:.2f} kg. "
        f"Masa grasa Johnston + masa muscular + masa ósea + masa residual = "
        f"{summary['component_total']:.2f} kg. "
        f"Diferencia: {summary['difference']:.2f} kg."
    )
    if not summary["is_warning"]:
        return f"{base} La suma de componentes es coherente frente al peso corporal."
    return (
        f"{base} La suma de componentes corporales presenta una diferencia significativa frente "
        "al peso corporal. Revise los datos ingresados o las ecuaciones aplicadas."
    )


def build_metric_card(label, value, unit="", helper=None, color=theme.PRIMARY_COLOR):
    value_text = f"{format_number(value)} {unit}".strip() if value is not None else "---"
    controls = [
        ft.Text(label, size=11, color=theme.SUBTITLE_COLOR),
        ft.Text(value_text, size=18, weight=ft.FontWeight.BOLD, color=color),
    ]
    if helper:
        controls.append(ft.Text(helper, size=10, color=theme.SUBTITLE_COLOR))
    return ft.Container(
        content=ft.Column(controls, spacing=4, tight=True),
        col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
        padding=12,
        bgcolor=theme.SURFACE_MUTED,
        border_radius=theme.RADIUS_SMALL,
        border=ft.border.all(1, theme.SURFACE_BORDER),
    )


def build_section(title, subtitle, content, col=None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, color=theme.PRIMARY_COLOR, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=11, color=theme.SUBTITLE_COLOR) if subtitle else ft.Container(visible=False),
                content,
            ],
            spacing=8,
        ),
        col=col,
        padding=12,
        bgcolor=ft.Colors.WHITE,
        border_radius=theme.RADIUS_SMALL,
        border=ft.border.all(1, theme.SURFACE_BORDER),
    )


def build_fat_methods_table(rows):
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Método")),
            ft.DataColumn(ft.Text("Grasa %")),
            ft.DataColumn(ft.Text("Masa grasa kg")),
            ft.DataColumn(ft.Text("% del peso")),
            ft.DataColumn(ft.Text("Uso")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(row["method"], weight="bold" if row["method"] == "Johnston" else None)),
                    ft.DataCell(ft.Text(format_number(row["fat_percent"]))),
                    ft.DataCell(ft.Text(format_number(row["fat_mass"]))),
                    ft.DataCell(ft.Text(format_number(row["percent_of_weight"]))),
                    ft.DataCell(ft.Text(row["use"])),
                ]
            )
            for row in rows
        ],
        heading_row_color=theme.SURFACE_MUTED,
        data_row_color={"even": ft.Colors.WHITE, "odd": theme.SURFACE_MUTED},
        column_spacing=18,
    )
    return horizontal_scroll(table)


def build_composition_table(rows):
    fat_rows = [row for row in rows if row["component"] in ("Grasa corporal", "Masa grasa")]
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Componente")),
            ft.DataColumn(ft.Text("Valor")),
            ft.DataColumn(ft.Text("Unidad")),
            ft.DataColumn(ft.Text("Método")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(row["component"])),
                    ft.DataCell(ft.Text(format_number(row["value"]))),
                    ft.DataCell(ft.Text(row["unit"])),
                    ft.DataCell(ft.Text(row["method"], weight="bold" if row["method"] == "Johnston" else None)),
                ]
            )
            for row in fat_rows
        ],
        heading_row_color=theme.SURFACE_MUTED,
        data_row_color={"even": ft.Colors.WHITE, "odd": theme.SURFACE_MUTED},
        column_spacing=24,
    )
    return horizontal_scroll(table)


def build_mass_distribution_table(rows):
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Componente")),
            ft.DataColumn(ft.Text("kg")),
            ft.DataColumn(ft.Text("% peso")),
            ft.DataColumn(ft.Text("Rol")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(row["component"], weight="bold" if row.get("is_total") else None)),
                    ft.DataCell(ft.Text(format_number(row["value"]))),
                    ft.DataCell(ft.Text(format_number(row["percent"]))),
                    ft.DataCell(ft.Text(row["role"])),
                ]
            )
            for row in rows
        ],
        heading_row_color=theme.SURFACE_MUTED,
        data_row_color={"even": ft.Colors.WHITE, "odd": theme.SURFACE_MUTED},
        column_spacing=18,
    )
    return horizontal_scroll(table)


def build_status_banner(text, is_warning=False):
    color = ft.Colors.ORANGE_700 if is_warning else ft.Colors.GREEN_700
    background = ft.Colors.ORANGE_50 if is_warning else ft.Colors.GREEN_50
    icon = ft.Icons.WARNING_AMBER_ROUNDED if is_warning else ft.Icons.CHECK_CIRCLE_OUTLINE
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, color=color, size=18),
                ft.Text(text, size=12, color=theme.SUBTITLE_COLOR, expand=True),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=background,
        padding=10,
        border_radius=theme.RADIUS_SMALL,
        border=ft.border.all(1, ft.Colors.ORANGE_100 if is_warning else ft.Colors.GREEN_100),
    )


def build_mass_pie_chart(distribution_rows):
    component_rows = [
        row
        for row in distribution_rows
        if not row.get("is_total") and row["value"] is not None and row["value"] > 0
    ]
    if not component_rows:
        return ft.Text("No hay masas corporales disponibles para graficar.", color=theme.SUBTITLE_COLOR)

    sections = [
        ft.PieChartSection(
            value=row["value"],
            title=f"{row['percent']:.1f} %" if row["percent"] is not None else "",
            color=MASS_COLORS[index % len(MASS_COLORS)],
            radius=82,
            title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        )
        for index, row in enumerate(component_rows)
    ]
    legend = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(width=12, height=12, bgcolor=MASS_COLORS[index % len(MASS_COLORS)], border_radius=3),
                    ft.Text(f"{row['component']}: {row['value']:.2f} kg ({format_number(row['percent'])} %)", size=12),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            for index, row in enumerate(component_rows)
        ],
        spacing=6,
    )
    return ft.ResponsiveRow(
        [
            ft.Container(
                content=ft.PieChart(
                    sections=sections,
                    sections_space=2,
                    center_space_radius=36,
                    height=240,
                    width=240,
                ),
                col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
                alignment=ft.alignment.center,
            ),
            ft.Container(content=legend, col={"xs": 12, "sm": 12, "md": 12, "lg": 12}),
        ],
        spacing=12,
        run_spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def build_method_comparison(rows):
    percent_rows = [row for row in rows if row["kind"] == "percent" and parse_float(row["value"]) is not None]
    if len(percent_rows) < 2:
        return ft.Container(visible=False)
    values = [parse_float(row["value"]) for row in percent_rows]
    return ft.Text(
        f"Comparación entre métodos: mínimo {min(values):.2f} %, máximo {max(values):.2f} %, "
        f"diferencia {max(values) - min(values):.2f} %. Johnston se mantiene como referencia principal.",
        size=12,
        color=theme.SUBTITLE_COLOR,
    )


def build_composition_panel(detail):
    rows = build_composition_rows(detail)
    fat_method_rows = build_fat_method_rows(detail)
    distribution_rows = build_mass_distribution_rows(detail)
    balance = mass_balance_summary(detail)
    balance_text = mass_balance_message(balance)
    equation_warning = fat_equation_warning(detail)

    summary_cards = ft.ResponsiveRow(
        [
            build_metric_card("Masa grasa Johnston", detail.get("PesoGrasoJhonston"), "kg", "Método principal"),
            build_metric_card("Masa muscular", detail.get("Mma"), "kg", "Componente magro"),
            build_metric_card("Masa ósea", detail.get("PesoOseo"), "kg", "Componente estructural"),
            build_metric_card("Masa residual", detail.get("PesoResidual"), "kg", "Componente residual"),
        ],
        spacing=10,
        run_spacing=10,
    )

    alerts = []
    if balance_text:
        alerts.append(build_status_banner(balance_text, balance["is_warning"]))
    if equation_warning:
        alerts.append(build_status_banner(equation_warning, True))

    distribution_flow = ft.Column(
        [
            build_section(
                "Distribución del peso",
                "Peso corporal contra grasa, músculo, hueso y masa residual.",
                build_mass_distribution_table(distribution_rows),
            ),
            build_section(
                "Gráfico de masas",
                "Participación porcentual de cada componente corporal.",
                build_mass_pie_chart(distribution_rows),
            ),
        ],
        spacing=12,
    )

    controls = [
        summary_cards,
        build_section(
            "Métodos de grasa",
            "Johnston es el método principal; Faulkner y Yuhasz son referencias comparativas.",
            build_fat_methods_table(fat_method_rows),
        ),
    ]
    controls.extend(alerts)
    controls.extend(
        [
            distribution_flow,
            build_method_comparison(rows),
        ]
    )
    return ft.Column(controls, spacing=12)
