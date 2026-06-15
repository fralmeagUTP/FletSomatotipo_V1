import flet as ft

from src.frontend import theme
from src.frontend.components import danger_icon_button, edit_icon_button
from src.frontend.formatters import age_from_birth_date, display_value


def format_number(value, fallback="-"):
    if value in (None, ""):
        return fallback
    try:
        number = float(value)
    except (TypeError, ValueError):
        return display_value(value, fallback)
    return f"{number:.2f}".rstrip("0").rstrip(".")


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
                        edit_icon_button(on_click=lambda event, item=deportista: on_edit(item)),
                        danger_icon_button(on_click=lambda event, item_id=identi: on_delete(item_id)),
                    ]
                )
            ),
        ]
    )


def build_measurement_row(detail: dict, on_delete, on_edit=None, index=None):
    actions = []
    if on_edit is not None:
        actions.append(
            edit_icon_button(
                tooltip="Editar medición",
                on_click=lambda event, item=detail: on_edit(item),
            )
        )
    actions.append(
        danger_icon_button(
            tooltip="Eliminar medición",
            on_click=lambda event, item=detail: on_delete(item),
        )
    )
    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(f"#{index}" if index is not None else display_value(detail.get("ID"), "-"))),
            ft.DataCell(ft.Text(str(detail["PESO_kg"]))),
            ft.DataCell(ft.Text(str(detail["ESTA_USER_CM"]))),
            ft.DataCell(ft.Text(f"Tri:{detail['PLIEGUE_TRICIPITAL']} Sub:{detail['PLIEGUE_SUBESCAPULAR']}...")),
            ft.DataCell(ft.Row(actions, spacing=0)),
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
                "PESO_kg": row.get("PESO_kg"),
                "IMC": row.get("IMC"),
                "Complexion": row.get("Complexion"),
                "TipoComplexion": row.get("TipoComplexion"),
                "Endomorfismo": row.get("Endomorfismo"),
                "Mesomorfismo": row.get("Mesomorfismo"),
                "Ectomorfismo": row.get("Ectomorfismo"),
                "detalles": [],
            }
        grouped[sid]["detalles"].append(row)
    return grouped


def build_historial_item(somatotipo_id, item: dict, on_select, on_delete):
    summary_parts = [f"ID: {somatotipo_id}"]
    if item.get("PESO_kg") is not None:
        summary_parts.append(f"Peso: {format_number(item['PESO_kg'])} kg")
    if item.get("IMC") is not None:
        summary_parts.append(f"IMC: {format_number(item['IMC'])}")
    complexion = display_value(item.get("TipoComplexion"), "")
    complexion_value = format_number(item.get("Complexion"), "")
    if complexion or complexion_value:
        detail = f"{complexion_value} ({complexion})" if complexion and complexion_value else complexion or complexion_value
        summary_parts.append(f"Complexión física: {detail}")
    somatotype_values = [
        format_number(item.get("Endomorfismo"), ""),
        format_number(item.get("Mesomorfismo"), ""),
        format_number(item.get("Ectomorfismo"), ""),
    ]
    if any(somatotype_values):
        summary_parts.append(f"Somatotipo: {' - '.join(value or '-' for value in somatotype_values)}")
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(f"Fecha: {item['FECHA_MEDIDA']}", weight="bold"),
                ft.Text(item["NOMBRE_DEPORTISTA"], size=12, no_wrap=True, color=theme.SUBTITLE_COLOR),
                ft.Text(" · ".join(summary_parts), size=11, color=theme.SUBTITLE_COLOR),
            ],
        ),
        padding=10,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        on_click=lambda event, selected=item: on_select(selected),
        ink=True,
        border=ft.border.all(1, "#dddddd"),
    )
