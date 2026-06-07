import flet as ft

from src.frontend import theme
from src.frontend.formatters import age_from_birth_date, display_value


def build_deportista_row(deportista: dict, on_edit, on_delete):
    identi = deportista["IDENTI_DEPORTISTA"]
    contact = display_value(deportista.get("E_MAIL"), display_value(deportista.get("TELEFONO")))
    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(str(identi))),
            ft.DataCell(ft.Text(deportista["NOMBRE_DEPORTISTA"])),
            ft.DataCell(ft.Text(deportista["SEXO_DEPORTISTA"])),
            ft.DataCell(ft.Text(age_from_birth_date(deportista.get("FECHA_NAC")))),
            ft.DataCell(ft.Text(display_value(deportista.get("CIUDAD_RESI")))),
            ft.DataCell(ft.Text(contact, no_wrap=True)),
            ft.DataCell(
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.EDIT,
                            icon_color=theme.PRIMARY_COLOR,
                            on_click=lambda event, item=deportista: on_edit(item),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            icon_color="red",
                            on_click=lambda event, item_id=identi: on_delete(item_id),
                        ),
                    ]
                )
            ),
        ]
    )


def build_measurement_row(detail: dict, on_delete):
    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(str(detail["PESO_kg"]))),
            ft.DataCell(ft.Text(str(detail["ESTA_USER_CM"]))),
            ft.DataCell(ft.Text(f"Tri:{detail['PLIEGUE_TRICIPITAL']} Sub:{detail['PLIEGUE_SUBESCAPULAR']}...")),
            ft.DataCell(
                ft.IconButton(
                    ft.Icons.DELETE,
                    icon_color="red",
                    on_click=lambda event, item=detail: on_delete(item),
                )
            ),
        ]
    )


def group_historial_rows(rows: list[dict]):
    grouped = {}
    for row in rows:
        sid = row["id_Somatotipo"]
        if sid not in grouped:
            grouped[sid] = {
                "FECHA_MEDIDA": row["FECHA_MEDIDA"],
                "NOMBRE_DEPORTISTA": row.get("NOMBRE_DEPORTISTA", ""),
                "EDAD": row.get("EDAD"),
                "SEXO_DEPORTISTA": row.get("SEXO_DEPORTISTA"),
                "detalles": [],
            }
        grouped[sid]["detalles"].append(row)
    return grouped


def build_historial_item(somatotipo_id, item: dict, on_select, on_delete):
    return ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(f"Fecha: {item['FECHA_MEDIDA']}", weight="bold"),
                        ft.Text(item["NOMBRE_DEPORTISTA"], size=12, no_wrap=True, color=theme.SUBTITLE_COLOR),
                    ],
                    expand=True,
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color="red",
                    tooltip="Eliminar Evaluación",
                    on_click=lambda event, item_id=somatotipo_id: on_delete(item_id),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=10,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        on_click=lambda event, selected=item: on_select(selected),
        ink=True,
        border=ft.border.all(1, "#dddddd"),
    )
