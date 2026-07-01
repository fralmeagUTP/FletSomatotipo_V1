import flet as ft
from datetime import datetime

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


def AsignacionesView(page: ft.Page):
    api = ApiClient(page)
    current_edit_id = None
    selected_athlete = None
    current_page = 1
    page_size = 10
    total_count = 0
    deportes = []
    entidades = []
    deportistas_por_id = {}

    athlete_search = ft.TextField(label="Buscar deportista por ID o nombre", suffix_icon=ft.Icons.SEARCH)
    deporte_dropdown = ft.Dropdown(label="Deporte")
    entidad_dropdown = ft.Dropdown(label="Entidad")
    search_field = ft.TextField(label="Buscar asignación", suffix_icon=ft.Icons.SEARCH)
    status_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    rows_container = ft.Column(spacing=8)
    mobile_rows = ft.Column(spacing=8)
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=12)
    save_button = primary_button("Guardar asignacion", icon=ft.Icons.SAVE)
    cancel_button = secondary_button("Cancelar edicion", icon=ft.Icons.CANCEL, visible=False)

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
        bgcolor=theme.INFO_BACKGROUND,
        border_radius=theme.RADIUS_MEDIUM,
        padding=12,
        visible=False,
    )

    athlete_info_text = ft.Text("Selecciona un deportista para asignarlo.", color=theme.SUBTITLE_COLOR, size=13)
    mobile_info_id = ft.Text("ID: -", size=11, color=theme.SUBTITLE_COLOR)
    mobile_info_nombre = ft.Text(
        "-",
        size=14,
        weight=ft.FontWeight.BOLD,
        color=theme.TEXT_COLOR,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )
    mobile_info_edad = ft.Text("Edad: -", size=12, color=theme.SUBTITLE_COLOR)
    mobile_info_email = ft.Text("Email: -", size=12, color=theme.SUBTITLE_COLOR, max_lines=2)
    mobile_info_ubicacion = ft.Text("Ubicación: -", size=12, color=theme.SUBTITLE_COLOR, max_lines=2)
    mobile_info_direccion = ft.Text("Dirección: -", size=12, color=theme.SUBTITLE_COLOR, max_lines=2)
    mobile_athlete_info_container = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON_OUTLINE, color=theme.PRIMARY_COLOR, size=24),
                            width=42,
                            height=42,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=21,
                            alignment=ft.alignment.center,
                        ),
                        ft.Column([mobile_info_nombre, mobile_info_id], spacing=2, expand=True),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=8, color=theme.SURFACE_BORDER),
                mobile_info_edad,
                mobile_info_email,
                mobile_info_ubicacion,
                mobile_info_direccion,
            ],
            spacing=5,
        ),
        bgcolor=theme.INFO_BACKGROUND,
        border_radius=theme.RADIUS_MEDIUM,
        padding=12,
        visible=False,
    )

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
        nonlocal deportes, entidades, deportistas_por_id
        try:
            deportes = api.list_deportes(page_size=100)
            entidades = api.list_entidades(page_size=100)
            deportistas = api.list_deportistas("", 1, 100)
            deportistas_por_id = {
                str(item.get("IDENTI_DEPORTISTA")): item
                for item in deportistas
                if item.get("IDENTI_DEPORTISTA")
            }
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

    def athlete_name(athlete_id):
        athlete = deportistas_por_id.get(str(athlete_id)) or {}
        return athlete.get("NOMBRE_DEPORTISTA") or str(athlete_id or "Deportista")

    def clear_form():
        nonlocal current_edit_id, selected_athlete
        current_edit_id = None
        selected_athlete = None
        athlete_search.value = ""
        athlete_info_text.visible = True
        athlete_info_container.visible = False
        mobile_athlete_info_container.visible = False
        deporte_dropdown.value = None
        entidad_dropdown.value = None
        save_button.text = "Guardar asignación"
        cancel_button.visible = False

    def payload():
        if not selected_athlete:
            raise ValueError("Debe seleccionar un deportista")
        if not deporte_dropdown.value:
            raise ValueError("Debe seleccionar un deporte")
        if not entidad_dropdown.value:
            raise ValueError("Debe seleccionar una entidad")
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
        mobile_info_id.value = f"ID: {athlete.get('IDENTI_DEPORTISTA', '-')}"
        mobile_info_nombre.value = athlete.get("NOMBRE_DEPORTISTA", "-")
        mobile_info_edad.value = f"Edad: {calculate_age(athlete.get('FECHA_NAC'))}"
        mobile_info_email.value = f"Email: {athlete.get('E_MAIL') or 'N/A'}"
        city = athlete.get("CIUDAD_RESI") or "N/A"
        department = athlete.get("DEPARTA_RESI") or "N/A"
        mobile_info_ubicacion.value = f"Ubicación: {city}, {department}"
        mobile_info_direccion.value = f"Dirección: {athlete.get('DIRECC_RESI') or 'N/A'}"
        mobile_athlete_info_container.visible = True

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
                mobile_athlete_info_container.visible = False
            else:
                exact_match = next(
                    (
                        item for item in matches
                        if str(item.get("IDENTI_DEPORTISTA")) == str(query).strip()
                    ),
                    None,
                )
                selected_athlete = exact_match or matches[0]
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
        athlete_id = str(item["IDENTI_DEPORTISTA"])
        selected_athlete = deportistas_por_id.get(athlete_id)
        if selected_athlete is None:
            try:
                matches = api.list_deportistas(athlete_id, 1, 20)
                selected_athlete = next(
                    (
                        athlete for athlete in matches
                        if str(athlete.get("IDENTI_DEPORTISTA")) == athlete_id
                    ),
                    None,
                )
            except ApiError as error:
                show_snack(page, str(error))
        if selected_athlete is None:
            selected_athlete = {
                "IDENTI_DEPORTISTA": athlete_id,
                "NOMBRE_DEPORTISTA": item.get("NOMBRE_DEPORTISTA") or athlete_name(athlete_id),
            }
        athlete_search.value = item["IDENTI_DEPORTISTA"]
        update_athlete_card(selected_athlete)
        deporte_dropdown.value = str(item["ID_DEPORTE"])
        entidad_dropdown.value = item["NIT_ENTIDAD"]
        save_button.text = "Actualizar asignación"
        cancel_button.visible = True
        if is_mobile(page):
            open_mobile_form(editing=True)
        page.update()

    def delete_item(item_id):
        try:
            api.delete_asignacion(item_id)
            if current_edit_id == item_id:
                close_mobile_form()
                clear_form()
            load_asignaciones(search_field.value or "", current_page)
            show_snack(page, "Asignación eliminada")
        except ApiError as error:
            show_snack(page, str(error))

    def confirm_delete(item_id):
        page.open(
            confirm_delete_dialog(
                "Eliminar asignacion",
                f"¿Seguro que deseas eliminar la asignacion {item_id}?",
                lambda _: delete_item(item_id),
                page=page,
            )
        )

    def render_rows(items):
        rows_container.controls.clear()
        mobile_rows.controls.clear()
        for item in items:
            display_athlete_name = item.get("NOMBRE_DEPORTISTA") or athlete_name(item.get("IDENTI_DEPORTISTA"))
            sport_name = deporte_name(item.get("ID_DEPORTE"))
            organization_name = entidad_name(item.get("NIT_ENTIDAD"))
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
                                        edit_icon_button(on_click=lambda e, data=item: edit_item(data)),
                                        danger_icon_button(on_click=lambda e, item_id=item["id"]: confirm_delete(item_id)),
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
                    display_athlete_name,
                    f"{sport_name} · {organization_name}",
                    display_athlete_name,
                    "#ede9fe",
                    on_click=lambda e, data=item: edit_item(data),
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
            close_mobile_form()
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
        title=ft.Text("Nueva asignación"),
        content=ft.Container(
            content=ft.Column(
                [
                    athlete_search,
                    athlete_info_text,
                    mobile_athlete_info_container,
                    deporte_dropdown,
                    entidad_dropdown,
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=350,
            height=470,
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
        mobile_form_dialog.title.value = "Editar asignación" if editing else "Nueva asignación"
        mobile_delete_button.visible = editing
        if mobile_form_dialog not in page.overlay:
            page.overlay.append(mobile_form_dialog)
        mobile_form_dialog.open = True
        page.update()

    mobile_cancel_button.on_click = lambda _: (close_mobile_form(), clear_form(), page.update())
    mobile_save_button.on_click = save_item
    mobile_delete_button.on_click = lambda _: confirm_delete(current_edit_id)

    load_catalogs()
    load_asignaciones()

    if is_mobile(page):
        def search_mobile(query):
            search_field.value = query
            load_asignaciones(query, 1)

        mobile_search = mobile_search_field("Buscar asignaciones...", on_search=search_mobile)
        return mobile_screen(
            ft.Column(
                [
                    mobile_search,
                    mobile_primary_button("Nueva asignación", on_click=lambda _: open_mobile_form()),
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
                section_title("Asignar deportista a deporte y entidad"),
                athlete_search,
                deporte_dropdown,
                entidad_dropdown,
                athlete_info_text,
                athlete_info_container,
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
                        section_title("Asignaciones registradas"),
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
                page_header("Asignaciones Deportivas", on_back=lambda e: show_dashboard(page), color=theme.HEADING_COLOR),
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
