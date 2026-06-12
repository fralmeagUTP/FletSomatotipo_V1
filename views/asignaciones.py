import flet as ft
from datetime import datetime

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import page_header, responsive_padding, section_title, set_busy
from src.frontend.navigation import show_dashboard


def AsignacionesView(page: ft.Page):
    api = ApiClient(page)
    current_edit_id = None
    selected_athlete = None
    current_page = 1
    page_size = 10
    total_count = 0
    deportes = []
    entidades = []

    athlete_search = ft.TextField(label="Buscar deportista por ID o nombre", suffix_icon=ft.Icons.SEARCH)
    deporte_dropdown = ft.Dropdown(label="Deporte")
    entidad_dropdown = ft.Dropdown(label="Entidad")
    search_field = ft.TextField(label="Buscar asignación", suffix_icon=ft.Icons.SEARCH)
    status_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    rows_container = ft.Column(spacing=8)
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=12)
    save_button = ft.ElevatedButton("Guardar asignación", icon=ft.Icons.SAVE, bgcolor=theme.PRIMARY_COLOR, color="white")
    cancel_button = ft.OutlinedButton("Cancelar edición", icon=ft.Icons.CANCEL, visible=False)

    # Athlete info card components
    athlete_photo = ft.Image(
        src="https://via.placeholder.com/120",
        width=120,
        height=120,
        fit=ft.ImageFit.COVER,
        border_radius=10,
    )
    info_id = ft.Text("-", size=12, color=theme.SUBTITLE_COLOR)
    info_nombre = ft.Text("-", weight="bold", size=16)
    info_edad = ft.Text("-", size=13)
    info_direccion = ft.Text("-", size=13)
    info_email = ft.Text("-", size=13)
    info_ciudad = ft.Text("-", size=13)
    info_depto = ft.Text("-", size=13)

    athlete_info_container = ft.Container(
        content=ft.Row(
            [
                ft.Container(content=athlete_photo, padding=ft.padding.all(4)),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Text("ID:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_id], spacing=4),
                            ft.Row([ft.Text("Nombre:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_nombre], spacing=4),
                            ft.ResponsiveRow([
                                ft.Container(ft.Row([ft.Text("Edad:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_edad], spacing=4), col={"xs": 6, "sm": 4}),
                                ft.Container(ft.Row([ft.Text("Email:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_email], spacing=4), col={"xs": 6, "sm": 8}),
                            ]),
                            ft.Row([ft.Text("Dirección:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_direccion], spacing=4),
                            ft.ResponsiveRow([
                                ft.Container(ft.Row([ft.Text("Ciudad:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_ciudad], spacing=4), col={"xs": 6, "sm": 6}),
                                ft.Container(ft.Row([ft.Text("Depto:", weight="bold", size=12, color=theme.SUBTITLE_COLOR), info_depto], spacing=4), col={"xs": 6, "sm": 6}),
                            ]),
                        ],
                        spacing=4,
                    ),
                    expand=True,
                    padding=ft.padding.only(left=8),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=12,
        visible=False,
    )

    athlete_info_text = ft.Text("Selecciona un deportista para asignarlo.", color=theme.SUBTITLE_COLOR, size=13)

    def calculate_age(birth_date_str):
        if not birth_date_str:
            return "Sin fecha nacimiento"
        try:
            birth = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return f"{age} años"
        except Exception:
            return "Error Calc."

    def load_catalogs():
        nonlocal deportes, entidades
        try:
            deportes = api.list_deportes(page_size=100)
            entidades = api.list_entidades(page_size=100)
            deporte_dropdown.options = [
                ft.dropdown.Option(str(item["ID_DEPORTE"]), item["DEPORTE"])
                for item in deportes
            ]
            entidad_dropdown.options = [
                ft.dropdown.Option(item["NIT_ENTIDAD"], item["RAZON_SOCIAL"])
                for item in entidades
            ]
        except ApiError as error:
            show_snack(page, str(error))

    def deporte_name(deporte_id):
        for item in deportes:
            if str(item.get("ID_DEPORTE")) == str(deporte_id):
                return item.get("DEPORTE")
        return str(deporte_id)

    def entidad_name(nit):
        for item in entidades:
            if item.get("NIT_ENTIDAD") == nit:
                return item.get("RAZON_SOCIAL")
        return nit

    def clear_form():
        nonlocal current_edit_id, selected_athlete
        current_edit_id = None
        selected_athlete = None
        athlete_search.value = ""
        athlete_info_text.visible = True
        athlete_info_container.visible = False
        deporte_dropdown.value = None
        entidad_dropdown.value = None
        save_button.text = "Guardar asignación"
        cancel_button.visible = False

    def payload():
        if not selected_athlete:
            raise ValueError("Debe seleccionar un deportista")
        return {
            "ID_DEPORTE": int(deporte_dropdown.value or 0),
            "IDENTI_DEPORTISTA": selected_athlete["IDENTI_DEPORTISTA"],
            "NIT_ENTIDAD": entidad_dropdown.value or "",
        }

    def update_athlete_card(athlete):
        info_id.value = athlete.get("IDENTI_DEPORTISTA", "-")
        info_nombre.value = athlete.get("NOMBRE_DEPORTISTA", "-")
        info_edad.value = calculate_age(athlete.get("FECHA_NAC"))
        info_direccion.value = athlete.get("DIRECC_RESI") or "N/A"
        info_email.value = athlete.get("E_MAIL") or "N/A"
        info_ciudad.value = athlete.get("CIUDAD_RESI") or "N/A"
        info_depto.value = athlete.get("DEPARTA_RESI") or "N/A"
        foto_url = athlete.get("FOTO_DEPORTISTA")
        athlete_photo.src = foto_url if foto_url else "https://via.placeholder.com/120"
        athlete_info_text.visible = False
        athlete_info_container.visible = True

    def search_athlete(_=None):
        nonlocal selected_athlete
        query = athlete_search.value or ""
        if not query:
            return
        try:
            matches = api.list_deportistas(query)
            if not matches:
                selected_athlete = None
                athlete_info_text.value = "No se encontraron deportistas."
                athlete_info_text.color = theme.ERROR_COLOR
                athlete_info_text.visible = True
                athlete_info_container.visible = False
            else:
                selected_athlete = matches[0]
                update_athlete_card(selected_athlete)
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def load_asignaciones(search="", page_number=1):
        nonlocal current_page, total_count
        try:
            result = api.list_asignaciones_page(search, page_number, page_size)
            current_page = result.get("page", page_number)
            total_count = result.get("total", 0)
            render_rows(result.get("items", []))
            pagination_text.value = f"Página {current_page} | Total: {total_count}"
            status_text.value = "Sin asignaciones registradas." if total_count == 0 else ""
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def edit_item(item):
        nonlocal current_edit_id, selected_athlete
        current_edit_id = item["id"]
        selected_athlete = {
            "IDENTI_DEPORTISTA": item["IDENTI_DEPORTISTA"],
            "NOMBRE_DEPORTISTA": item.get("NOMBRE_DEPORTISTA", item["IDENTI_DEPORTISTA"]),
        }
        athlete_search.value = item["IDENTI_DEPORTISTA"]
        update_athlete_card(selected_athlete)
        deporte_dropdown.value = str(item["ID_DEPORTE"])
        entidad_dropdown.value = item["NIT_ENTIDAD"]
        save_button.text = "Actualizar asignación"
        cancel_button.visible = True
        page.update()

    def delete_item(item_id):
        try:
            api.delete_asignacion(item_id)
            if current_edit_id == item_id:
                clear_form()
            load_asignaciones(search_field.value or "", current_page)
            show_snack(page, "Asignación eliminada")
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
                                        ft.Icon(ft.Icons.LINK, color=theme.PRIMARY_COLOR, size=24),
                                        ft.Column(
                                            [
                                                ft.Text(deporte_name(item.get("ID_DEPORTE")), weight="bold", color=theme.TEXT_COLOR, size=14),
                                                ft.Text(f"Deportista: {item.get('IDENTI_DEPORTISTA')} | Entidad: {entidad_name(item.get('NIT_ENTIDAD'))}", size=12, color=theme.SUBTITLE_COLOR),
                                                ft.Text(f"ID: {item.get('id')}", size=11, color=theme.SUBTITLE_COLOR),
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
                                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=theme.ERROR_COLOR, tooltip="Eliminar", on_click=lambda e, item_id=item["id"]: delete_item(item_id)),
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
                api.update_asignacion(current_edit_id, data)
                show_snack(page, "Asignación actualizada")
            else:
                api.create_asignacion(data)
                show_snack(page, "Asignación creada")
            clear_form()
            load_asignaciones(search_field.value or "", current_page)
        except ValueError as error:
            show_snack(page, str(error))
        except ApiError as error:
            show_snack(page, str(error))
        finally:
            set_busy(page, [save_button, cancel_button], False)

    def previous_page(_):
        if current_page > 1:
            load_asignaciones(search_field.value or "", current_page - 1)

    def next_page(_):
        if current_page * page_size < total_count:
            load_asignaciones(search_field.value or "", current_page + 1)

    athlete_search.on_submit = search_athlete
    save_button.on_click = save_item
    cancel_button.on_click = lambda _: (clear_form(), page.update())
    search_field.on_submit = lambda e: load_asignaciones(e.control.value, 1)

    load_catalogs()
    load_asignaciones()

    return ft.Container(
        content=ft.Column(
            [
                page_header("Asignaciones Deportivas", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
                ft.Container(
                    content=ft.Column(
                        [
                            section_title("Asignar deportista a deporte y entidad"),
                            ft.ResponsiveRow(
                                [
                                    ft.Container(content=athlete_search, col={"xs": 12, "sm": 6, "md": 5}),
                                    ft.Container(content=deporte_dropdown, col={"xs": 12, "sm": 3, "md": 3}),
                                    ft.Container(content=entidad_dropdown, col={"xs": 12, "sm": 3, "md": 4}),
                                ],
                                spacing=10,
                                run_spacing=10,
                            ),
                            athlete_info_text,
                            athlete_info_container,
                            ft.Row([cancel_button, save_button], alignment=ft.MainAxisAlignment.END),
                            ft.Divider(),
                            section_title("Asignaciones registradas"),
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
