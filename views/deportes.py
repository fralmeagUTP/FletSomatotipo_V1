import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import page_header, responsive_padding, section_title, set_busy
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
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=12)
    save_button = ft.ElevatedButton("Guardar deporte", icon=ft.Icons.SAVE, bgcolor=theme.PRIMARY_COLOR, color="white")
    cancel_button = ft.OutlinedButton("Cancelar edición", icon=ft.Icons.CANCEL, visible=False)

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
        page.update()

    def delete_item(item_id):
        try:
            api.delete_deporte(item_id)
            if current_edit_id == item_id:
                clear_form()
            load_deportes(search_field.value or "", current_page)
            show_snack(page, "Deporte eliminado")
        except ApiError as error:
            show_snack(page, str(error))

    def render_rows(items):
        rows_container.controls.clear()
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
                                        ft.IconButton(ft.Icons.EDIT, icon_color=theme.PRIMARY_COLOR, tooltip="Editar", on_click=lambda e, data=item: edit_item(data)),
                                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=theme.ERROR_COLOR, tooltip="Eliminar", on_click=lambda e, item_id=item["ID_DEPORTE"]: delete_item(item_id)),
                                    ],
                                    spacing=4,
                                ),
                                col={"xs": 12, "sm": 4, "md": 3},
                                alignment=ft.alignment.center_right,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, "#e3e8f0"),
                    border_radius=10,
                    padding=12,
                )
            )

    def save_item(_):
        set_busy(page, [save_button, cancel_button], True)
        try:
            data = payload()
            if current_edit_id:
                api.update_deporte(current_edit_id, data)
                show_snack(page, "Deporte actualizado")
            else:
                api.create_deporte(data)
                show_snack(page, "Deporte creado")
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

    load_deportes()

    return ft.Container(
        content=ft.Column(
            [
                page_header("Deportes", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
                ft.Container(
                    content=ft.Column(
                        [
                            section_title("Datos del deporte"),
                            ft.ResponsiveRow(
                                [
                                    ft.Container(content=deporte_id, col={"xs": 12, "sm": 4, "md": 3}),
                                    ft.Container(content=nombre, col={"xs": 12, "sm": 8, "md": 9}),
                                ],
                                spacing=10,
                                run_spacing=10,
                            ),
                            ft.Row([cancel_button, save_button], alignment=ft.MainAxisAlignment.END),
                            ft.Divider(),
                            section_title("Deportes registrados"),
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
                    border_radius=12,
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
