import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import (
    confirm_delete_dialog,
    danger_icon_button,
    edit_icon_button,
    is_mobile,
    mobile_list_card,
    mobile_primary_button,
    mobile_screen,
    mobile_search_field,
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
    mobile_rows = ft.Column(spacing=8)

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
        if is_mobile(page):
            open_mobile_form(editing=True)
        page.update()

    def delete_item(item_id):
        try:
            api.delete_entidad(item_id)
            if current_edit_nit == item_id:
                close_mobile_form()
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
        mobile_rows.controls.clear()
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
            organization_name = item.get("RAZON_SOCIAL") or "Entidad sin nombre"
            mobile_rows.controls.append(
                mobile_list_card(
                    organization_name,
                    f"NIT: {item.get('NIT_ENTIDAD') or '-'}",
                    organization_name,
                    "#dcfce7",
                    on_click=lambda e, data=item: edit_item(data),
                )
            )

    def save_item(_):
        if not (nit.value or "").strip():
            show_snack(page, "El NIT es obligatorio")
            return
        if not (razon.value or "").strip():
            show_snack(page, "La razón social es obligatoria")
            return
        set_busy(page, [save_button, cancel_button], True)
        try:
            data = payload()
            if current_edit_nit:
                api.update_entidad(current_edit_nit, data)
                show_snack(page, "Entidad actualizada")
            else:
                api.create_entidad(data)
                show_snack(page, "Entidad creada")
            close_mobile_form()
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

    mobile_delete_button = ft.TextButton(
        "Eliminar",
        icon=ft.Icons.DELETE_OUTLINE,
        style=ft.ButtonStyle(color=theme.ERROR_COLOR),
        visible=False,
    )
    mobile_cancel_button = ft.TextButton("Cancelar")
    mobile_save_button = primary_button("Guardar", icon=ft.Icons.SAVE)
    mobile_form_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nueva entidad"),
        content=ft.Container(
            content=ft.Column(
                [nit, razon, telefono, contacto, email],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=350,
            height=390,
        ),
        actions=[mobile_delete_button, mobile_cancel_button, mobile_save_button],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_mobile_form(_=None):
        if not mobile_form_dialog.open:
            return
        try:
            page.close(mobile_form_dialog)
        except Exception:
            mobile_form_dialog.open = False
            page.update()

    def open_mobile_form(editing=False):
        if not editing:
            clear_form()
        mobile_form_dialog.title.value = "Editar entidad" if editing else "Nueva entidad"
        mobile_delete_button.visible = editing
        if mobile_form_dialog not in page.overlay:
            page.overlay.append(mobile_form_dialog)
        mobile_form_dialog.open = True
        page.update()

    mobile_cancel_button.on_click = lambda _: (close_mobile_form(), clear_form(), page.update())
    mobile_save_button.on_click = save_item
    mobile_delete_button.on_click = lambda _: confirm_delete(current_edit_nit)

    load_entidades()

    if is_mobile(page):
        def search_mobile(query):
            search_field.value = query
            load_entidades(query, 1)

        mobile_search = mobile_search_field("Buscar entidades...", on_search=search_mobile)
        return mobile_screen(
            ft.Column(
                [
                    mobile_search,
                    mobile_primary_button("Agregar entidad", on_click=lambda _: open_mobile_form()),
                    status_text,
                    mobile_rows,
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=previous_page),
                            pagination_text,
                            ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_page),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    form_panel = ft.Container(
        content=ft.Column(
            [
                section_title("Datos de la entidad"),
                nit,
                razon,
                ft.ResponsiveRow(
                    [
                        ft.Container(content=telefono, col={"xs": 12, "md": 6}),
                        ft.Container(content=contacto, col={"xs": 12, "md": 6}),
                    ],
                    spacing=10,
                    run_spacing=10,
                ),
                email,
                ft.Row([cancel_button, save_button], alignment=ft.MainAxisAlignment.END, wrap=True),
            ],
            spacing=12,
        ),
        bgcolor=theme.CARD_BACKGROUND,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=theme.RADIUS_MEDIUM,
        padding=18,
        shadow=theme.card_shadow(),
    )
    list_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        section_title("Entidades registradas"),
                        ft.Container(expand=True),
                        pagination_text,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                search_field,
                status_text,
                rows_container,
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=previous_page),
                        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_page),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=12,
        ),
        bgcolor=theme.CARD_BACKGROUND,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=theme.RADIUS_MEDIUM,
        padding=18,
        shadow=theme.card_shadow(),
    )

    return ft.Container(
        content=ft.Column(
            [
                page_header("Entidades", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
                ft.ResponsiveRow(
                    [
                        ft.Container(form_panel, col={"xs": 12, "lg": 4}),
                        ft.Container(list_panel, col={"xs": 12, "lg": 8}),
                    ],
                    spacing=14,
                    run_spacing=14,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
        ),
        bgcolor=theme.BACKGROUND_COLOR,
        padding=responsive_padding(page),
        expand=True,
    )
