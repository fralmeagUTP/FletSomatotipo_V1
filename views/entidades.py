import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import (
    confirm_delete_dialog,
    danger_icon_button,
    edit_icon_button,
    page_header,
    primary_button,
    responsive_padding,
    secondary_button,
    section_title,
    set_busy,
)
from src.frontend.navigation import show_dashboard


def EntidadesView(page: ft.Page):
    api = ApiClient(page)
    current_edit_nit = None
    current_page = 1
    page_size = 10
    total_count = 0

    search_field = ft.TextField(label="Buscar entidad por NIT, razón social o contacto", suffix_icon=ft.Icons.SEARCH)
    nit = ft.TextField(label="NIT entidad")
    razon = ft.TextField(label="Razón social")
    telefono = ft.TextField(label="Teléfono")
    contacto = ft.TextField(label="Contacto")
    email = ft.TextField(label="Email")
    status_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    rows_container = ft.Column(spacing=8)

    save_button = primary_button("Guardar entidad", icon=ft.Icons.SAVE)
    cancel_button = secondary_button("Cancelar edicion", icon=ft.Icons.CANCEL, visible=False)
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=12)

    def clear_form():
        nonlocal current_edit_nit
        current_edit_nit = None
        for field in (nit, razon, telefono, contacto, email):
            field.value = ""
        nit.read_only = False
        save_button.text = "Guardar entidad"
        cancel_button.visible = False

    def payload():
        return {
            "NIT_ENTIDAD": (nit.value or "").strip(),
            "RAZON_SOCIAL": (razon.value or "").strip(),
            "TELEFONO": (telefono.value or "").strip() or None,
            "CONTACTO": (contacto.value or "").strip() or None,
            "E_MAIL": (email.value or "").strip() or None,
        }

    def load_entidades(search="", page_number=1):
        nonlocal current_page, total_count
        try:
            result = api.list_entidades_page(search, page_number, page_size)
            current_page = result.get("page", page_number)
            total_count = result.get("total", 0)
            render_rows(result.get("items", []))
            pagination_text.value = f"Página {current_page} | Total: {total_count}"
            status_text.value = "Sin entidades registradas." if total_count == 0 else ""
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def edit_item(item):
        nonlocal current_edit_nit
        current_edit_nit = item["NIT_ENTIDAD"]
        nit.value = item.get("NIT_ENTIDAD") or ""
        razon.value = item.get("RAZON_SOCIAL") or ""
        telefono.value = item.get("TELEFONO") or ""
        contacto.value = item.get("CONTACTO") or ""
        email.value = item.get("E_MAIL") or ""
        nit.read_only = True
        save_button.text = "Actualizar entidad"
        cancel_button.visible = True
        page.update()

    def delete_item(item_id):
        try:
            api.delete_entidad(item_id)
            if current_edit_nit == item_id:
                clear_form()
            load_entidades(search_field.value or "", current_page)
            show_snack(page, "Entidad eliminada")
        except ApiError as error:
            show_snack(page, str(error))

    def confirm_delete(item_id):
        page.open(
            confirm_delete_dialog(
                "Eliminar entidad",
                f"¿Seguro que deseas eliminar la entidad {item_id}?",
                lambda _: delete_item(item_id),
                page=page,
            )
        )

    def render_rows(items):
        rows_container.controls.clear()
        for item in items:
            rows_container.controls.append(
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Text(item.get("RAZON_SOCIAL") or "-", weight="bold", color=theme.TEXT_COLOR, size=14),
                                        ft.Text(f"NIT: {item.get('NIT_ENTIDAD')} | Contacto: {item.get('CONTACTO') or 'N/A'}", size=12, color=theme.SUBTITLE_COLOR),
                                        ft.Text(f"Tel: {item.get('TELEFONO') or 'N/A'} | Email: {item.get('E_MAIL') or 'N/A'}", size=12, color=theme.SUBTITLE_COLOR),
                                    ],
                                    spacing=2,
                                ),
                                col={"xs": 12, "sm": 8, "md": 9},
                            ),
                            ft.Container(
                                ft.Row(
                                    [
                                        edit_icon_button(on_click=lambda e, data=item: edit_item(data)),
                                        danger_icon_button(on_click=lambda e, item_id=item["NIT_ENTIDAD"]: confirm_delete(item_id)),
                                    ],
                                    spacing=4,
                                ),
                                col={"xs": 12, "sm": 4, "md": 3},
                                alignment=ft.alignment.center_right,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=theme.CARD_BACKGROUND,
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    border_radius=theme.RADIUS_MEDIUM,
                    padding=12,
                )
            )

    def save_item(_):
        set_busy(page, [save_button, cancel_button], True)
        try:
            data = payload()
            if current_edit_nit:
                api.update_entidad(current_edit_nit, data)
                show_snack(page, "Entidad actualizada")
            else:
                api.create_entidad(data)
                show_snack(page, "Entidad creada")
            clear_form()
            load_entidades(search_field.value or "", current_page)
        except ApiError as error:
            show_snack(page, str(error))
        finally:
            set_busy(page, [save_button, cancel_button], False)

    def previous_page(_):
        if current_page > 1:
            load_entidades(search_field.value or "", current_page - 1)

    def next_page(_):
        if current_page * page_size < total_count:
            load_entidades(search_field.value or "", current_page + 1)

    save_button.on_click = save_item
    cancel_button.on_click = lambda _: (clear_form(), page.update())
    search_field.on_submit = lambda e: load_entidades(e.control.value, 1)

    load_entidades()

    return ft.Container(
        content=ft.Column(
            [
                page_header("Entidades", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
                ft.Container(
                    content=ft.Column(
                        [
                            section_title("Datos de la entidad"),
                            ft.ResponsiveRow(
                                [
                                    ft.Container(content=nit, col={"xs": 12, "sm": 6, "md": 3}),
                                    ft.Container(content=razon, col={"xs": 12, "sm": 6, "md": 5}),
                                    ft.Container(content=telefono, col={"xs": 6, "sm": 6, "md": 2}),
                                    ft.Container(content=contacto, col={"xs": 6, "sm": 6, "md": 2}),
                                    ft.Container(content=email, col={"xs": 12, "sm": 12, "md": 4}),
                                ],
                                spacing=10,
                                run_spacing=10,
                            ),
                            ft.Row([cancel_button, save_button], alignment=ft.MainAxisAlignment.END),
                            ft.Divider(),
                            section_title("Entidades registradas"),
                            search_field,
                            status_text,
                            rows_container,
                            ft.Row(
                                [
                                    ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=previous_page),
                                    pagination_text,
                                    ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_page),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=14,
                    ),
                    bgcolor=theme.CARD_BACKGROUND,
                    border_radius=theme.RADIUS_LARGE,
                    padding=responsive_padding(page, desktop=24, tablet=18, mobile=12),
                    shadow=theme.card_shadow(),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
        ),
        bgcolor=theme.BACKGROUND_COLOR,
        padding=responsive_padding(page),
        expand=True,
    )
