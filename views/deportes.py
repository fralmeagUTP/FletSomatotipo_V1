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


def DeportesView(page: ft.Page):
    api = ApiClient(page)
    current_edit_id = None
    current_page = 1
    page_size = 10
    total_count = 0

    search_field = ft.TextField(label="Buscar deporte", suffix_icon=ft.Icons.SEARCH)
    deporte_id = ft.TextField(label="ID deporte (opcional)", keyboard_type=ft.KeyboardType.NUMBER)
    nombre = ft.TextField(label="Nombre del deporte")
    status_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    rows_container = ft.Column(spacing=8)
    mobile_rows = ft.Column(spacing=8)
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=12)
    save_button = primary_button("Guardar deporte", icon=ft.Icons.SAVE)
    cancel_button = secondary_button("Cancelar edicion", icon=ft.Icons.CANCEL, visible=False)

    def clear_form():
        nonlocal current_edit_id
        current_edit_id = None
        deporte_id.value = ""
        nombre.value = ""
        deporte_id.read_only = False
        save_button.text = "Guardar deporte"
        cancel_button.visible = False

    def payload():
        return {
            "ID_DEPORTE": int(deporte_id.value) if (deporte_id.value or "").strip() else None,
            "DEPORTE": (nombre.value or "").strip(),
        }

    def load_deportes(search="", page_number=1):
        nonlocal current_page, total_count
        try:
            result = api.list_deportes_page(search, page_number, page_size)
            current_page = result.get("page", page_number)
            total_count = result.get("total", 0)
            render_rows(result.get("items", []))
            pagination_text.value = f"Página {current_page} | Total: {total_count}"
            status_text.value = "Sin deportes registrados." if total_count == 0 else ""
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def edit_item(item):
        nonlocal current_edit_id
        current_edit_id = item["ID_DEPORTE"]
        deporte_id.value = str(item.get("ID_DEPORTE") or "")
        nombre.value = item.get("DEPORTE") or ""
        deporte_id.read_only = True
        save_button.text = "Actualizar deporte"
        cancel_button.visible = True
        if is_mobile(page):
            open_mobile_form(editing=True)
        page.update()

    def delete_item(item_id):
        try:
            api.delete_deporte(item_id)
            if current_edit_id == item_id:
                close_mobile_form()
                clear_form()
            load_deportes(search_field.value or "", current_page)
            show_snack(page, "Deporte eliminado")
        except ApiError as error:
            show_snack(page, str(error))

    def confirm_delete(item_id):
        page.open(
            confirm_delete_dialog(
                "Eliminar deporte",
                f"¿Seguro que deseas eliminar el deporte {item_id}?",
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
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SPORTS_SOCCER, color=theme.PRIMARY_COLOR, size=26),
                                        ft.Column(
                                            [
                                                ft.Text(item.get("DEPORTE") or "-", weight="bold", color=theme.TEXT_COLOR, size=14),
                                                ft.Text(f"ID: {item.get('ID_DEPORTE')}", size=12, color=theme.SUBTITLE_COLOR),
                                            ],
                                            spacing=2,
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                col={"xs": 12, "sm": 8, "md": 9},
                            ),
                            ft.Container(
                                ft.Row(
                                    [
                                        edit_icon_button(on_click=lambda e, data=item: edit_item(data)),
                                        danger_icon_button(on_click=lambda e, item_id=item["ID_DEPORTE"]: confirm_delete(item_id)),
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
            mobile_rows.controls.append(
                mobile_list_card(
                    item.get("DEPORTE") or "Sin nombre",
                    f"ID: {item.get('ID_DEPORTE') or '-'}",
                    item.get("DEPORTE") or "D",
                    "#dbeafe",
                    on_click=lambda e, data=item: edit_item(data),
                )
            )

    def save_item(_):
        if not (nombre.value or "").strip():
            show_snack(page, "El nombre del deporte es obligatorio")
            return
        set_busy(page, [save_button, cancel_button], True)
        try:
            data = payload()
            if current_edit_id:
                api.update_deporte(current_edit_id, data)
                show_snack(page, "Deporte actualizado")
            else:
                api.create_deporte(data)
                show_snack(page, "Deporte creado")
            close_mobile_form()
            clear_form()
            load_deportes(search_field.value or "", current_page)
        except ValueError:
            show_snack(page, "El ID debe ser numérico")
        except ApiError as error:
            show_snack(page, str(error))
        finally:
            set_busy(page, [save_button, cancel_button], False)

    def previous_page(_):
        if current_page > 1:
            load_deportes(search_field.value or "", current_page - 1)

    def next_page(_):
        if current_page * page_size < total_count:
            load_deportes(search_field.value or "", current_page + 1)

    save_button.on_click = save_item
    cancel_button.on_click = lambda _: (clear_form(), page.update())
    search_field.on_submit = lambda e: load_deportes(e.control.value, 1)

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
        title=ft.Text("Nuevo deporte"),
        content=ft.Container(
            content=ft.Column(
                [
                    deporte_id,
                    nombre,
                    ft.Text(
                        "El identificador es opcional al crear el deporte.",
                        size=11,
                        color=theme.SUBTITLE_COLOR,
                    ),
                ],
                spacing=12,
                tight=True,
            ),
            width=340,
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
        mobile_form_dialog.title.value = "Editar deporte" if editing else "Nuevo deporte"
        mobile_delete_button.visible = editing
        if mobile_form_dialog not in page.overlay:
            page.overlay.append(mobile_form_dialog)
        mobile_form_dialog.open = True
        page.update()

    mobile_cancel_button.on_click = lambda _: (close_mobile_form(), clear_form(), page.update())
    mobile_save_button.on_click = save_item
    mobile_delete_button.on_click = lambda _: confirm_delete(current_edit_id)

    load_deportes()

    if is_mobile(page):
        def search_mobile(event):
            search_field.value = event.control.value
            load_deportes(event.control.value, 1)

        mobile_search = mobile_search_field("Buscar deportes...", on_submit=search_mobile)

        return mobile_screen(
            ft.Column(
                [
                    mobile_search,
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
            bottom_action=mobile_primary_button("Agregar deporte", on_click=lambda _: open_mobile_form()),
        )

    form_panel = ft.Container(
        content=ft.Column(
            [
                section_title("Datos del deporte"),
                deporte_id,
                nombre,
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
                        section_title("Deportes registrados"),
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
                page_header("Deportes", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
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
