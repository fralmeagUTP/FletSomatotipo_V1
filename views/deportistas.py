import flet as ft
from datetime import datetime
from app_config import show_snack
from src.frontend.components import (
    content_card,
    empty_state as make_empty_state,
    is_mobile,
    mobile_list_card,
    mobile_primary_button,
    mobile_search_field,
    mobile_screen,
    page_header,
    responsive_dialog_size,
    responsive_padding,
    set_busy,
)
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.form_helpers import build_deportista_payload, required_missing
from src.frontend.navigation import show_dashboard
from src.frontend.table_builders import build_deportista_row
from src.frontend import theme

def DeportistasView(page: ft.Page):
    """
    Vista de Gestión de Deportistas.

    Permite listar, buscar, crear, editar y eliminar deportistas.
    Incluye un formulario en modal con pestañas para capturar toda la información detallada.

    Args:
        page (ft.Page): La referencia a la página principal de Flet.

    Returns:
        ft.Container: El contenedor principal con el diseño de la vista de deportistas.
    """
    # Colors
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    BG_COLOR = theme.BACKGROUND_COLOR
    CARD_BG = theme.CARD_BACKGROUND
    TEXT_COLOR = theme.TEXT_COLOR

    # State
    current_edit_id = None 
    selected_photo = None
    mobile_step = 0
    mobile_root = ft.Container(expand=True)
    api = ApiClient(page)

    def open_control(control):
        if control not in page.overlay:
            page.overlay.append(control)
        control.open = True
        page.update()

    def close_control(control):
        control.open = False
        page.update()

    # Catalogs
    tipos_documentos = []
    estratos = []
    niveles_educativos = []

    def load_catalogs():
        nonlocal tipos_documentos, estratos, niveles_educativos
        try:
            catalogs = api.get_catalogs()
            tipos_documentos = catalogs["tipos_documentos"]
            estratos = catalogs["estratos"]
            niveles_educativos = catalogs["niveles_educativos"]
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as error:
            show_snack(page, f"Error de conexion: {error}")

    load_catalogs()

    # --- Form Fields ---
    
    # Personal Info
    identi = ft.TextField(label="Identificación")
    tipo_identi = ft.Dropdown(
        label="Tipo Documento", 
        options=[ft.dropdown.Option(str(t['TIPO_IDENTI']), t['NOMBRE_IDENTI']) for t in tipos_documentos]
    )
    nombre = ft.TextField(label="Nombre Completo")
    sexo = ft.Dropdown(
        label="Sexo", 
        options=[ft.dropdown.Option("M", "Masculino"), ft.dropdown.Option("F", "Femenino")]
    )
    
    # Date Picker Logic
    fecha_nac = ft.TextField(label="Fecha Nacimiento", read_only=True)
    
    def on_date_change(e):
        if date_picker.value:
            fecha_nac.value = date_picker.value.strftime('%Y-%m-%d')
            fecha_nac.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(1900, 1, 1),
        # last_date=datetime.now(), # Removed to prevent timezone/time issues blocking "today"
    )
    
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)
        page.update()

    fecha_nac_btn = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: open_control(date_picker),
    )
    
    img_preview = ft.Image(
        src="https://via.placeholder.com/150", # Default placeholder
        width=150,
        height=150,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10)
    )
    photo_name = ft.Text("Sin foto nueva seleccionada", size=12, color=theme.SUBTITLE_COLOR)
    file_picker = ft.FilePicker()
    if not hasattr(page, "services"):
        page.services = []
    if file_picker not in page.services:
        page.services.append(file_picker)

    async def pick_photo(_):
        nonlocal selected_photo
        try:
            files = await file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE,
                with_data=True,
            )
            if not files:
                return
            selected_photo = files[0]
            if selected_photo.bytes is not None:
                img_preview.src = selected_photo.bytes
            elif selected_photo.path:
                img_preview.src = selected_photo.path
            else:
                selected_photo = None
                show_snack(page, "Android no permitió leer la foto seleccionada")
                return
            photo_name.value = selected_photo.name
            page.update()
        except Exception as error:
            show_snack(page, f"No se pudo seleccionar la foto: {error}")
            page.update()

    photo_button = ft.ElevatedButton(
        "Cargar o cambiar foto",
        icon=ft.Icons.ADD_A_PHOTO,
        on_click=pick_photo,
    )

    # Location - Birth
    pais_nac = ft.TextField(label="País Nacimiento")
    dep_nac = ft.TextField(label="Depto Nacimiento")
    ciudad_nac = ft.TextField(label="Ciudad Nacimiento")

    # Location - Residence & Contact
    dep_resi = ft.TextField(label="Depto Residencia")
    ciudad_resi = ft.TextField(label="Ciudad Residencia")
    direcc_resi = ft.TextField(label="Dirección")
    telefono = ft.TextField(label="Teléfono")
    email = ft.TextField(label="Email")

    # Socio-economic
    estrato_dd = ft.Dropdown(
        label="Estrato",
        options=[ft.dropdown.Option(str(e['ID_ESTRATO']), e['ESTRATO']) for e in estratos]
    )
    nivel_edu_dd = ft.Dropdown(
        label="Nivel Educativo",
        options=[ft.dropdown.Option(str(n['ID_NIVEL']), n['NIVEL_EDUCATIVO']) for n in niveles_educativos]
    )
    nombre_institu = ft.TextField(label="Institución")

    # Extra
    observaciones = ft.TextField(label="Observaciones", multiline=True, height=80)

    for field in [
        identi, tipo_identi, nombre, sexo, fecha_nac, pais_nac, dep_nac,
        ciudad_nac, dep_resi, ciudad_resi, direcc_resi, telefono, email,
        estrato_dd, nivel_edu_dd, nombre_institu, observaciones,
    ]:
        field.bgcolor = ft.Colors.WHITE
        field.border_color = theme.SURFACE_BORDER
        field.focused_border_color = PRIMARY_COLOR
        field.border_radius = theme.MOBILE_RADIUS

    deportista_fields = {
        "identi": identi,
        "tipo_identi": tipo_identi,
        "nombre": nombre,
        "sexo": sexo,
        "fecha_nac": fecha_nac,
        "pais_nac": pais_nac,
        "dep_nac": dep_nac,
        "ciudad_nac": ciudad_nac,
        "dep_resi": dep_resi,
        "ciudad_resi": ciudad_resi,
        "direcc_resi": direcc_resi,
        "telefono": telefono,
        "email": email,
        "estrato_dd": estrato_dd,
        "nivel_edu_dd": nivel_edu_dd,
        "nombre_institu": nombre_institu,
        "observaciones": observaciones,
    }

    search_field = ft.TextField(
        label="Buscar por nombre o ID", 
        suffix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: load_deportistas(e.control.value)
    )

    def clean_form():
        nonlocal current_edit_id, selected_photo
        current_edit_id = None
        selected_photo = None
        identi.value = ""
        identi.read_only = False
        tipo_identi.value = None
        nombre.value = ""
        sexo.value = None
        fecha_nac.value = ""
        img_preview.src = "https://via.placeholder.com/150"
        photo_name.value = "Sin foto nueva seleccionada"
        pais_nac.value = ""
        dep_nac.value = ""
        ciudad_nac.value = ""
        dep_resi.value = ""
        ciudad_resi.value = ""
        direcc_resi.value = ""
        telefono.value = ""
        email.value = ""
        estrato_dd.value = None
        nivel_edu_dd.value = None
        nombre_institu.value = ""
        observaciones.value = ""
        page.update()

    save_button = ft.ElevatedButton("Guardar")

    def save_deportista(e):
        required_fields = [
            (identi, "La identificacion es obligatoria"),
            (tipo_identi, "El tipo de documento es obligatorio"),
            (nombre, "El nombre es obligatorio"),
            (sexo, "El sexo es obligatorio"),
        ]
        missing_message = required_missing(required_fields)
        if missing_message:
            show_snack(page, missing_message)
            page.update()
            return

        set_busy(page, [save_button, photo_button], True)
        try:
            final_photo_url = img_preview.src
            if selected_photo is not None:
                final_photo_url = api.upload_photo(
                    file_path=selected_photo.path,
                    file_name=selected_photo.name,
                    file_bytes=selected_photo.bytes,
                )
            data = build_deportista_payload(deportista_fields, final_photo_url)

            if current_edit_id:
                # Update
                api.update_deportista(current_edit_id, data)
            else:
                # Create
                api.create_deportista(data)

            show_snack(page, "Deportista guardado exitosamente")
            clean_form()
            if is_mobile(page):
                show_mobile_list()
            else:
                close_control(dlg_modal)
            load_deportistas()
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as ex:
            show_snack(page, f"Error de conexion: {ex}")
        finally:
            set_busy(page, [save_button, photo_button], False)
        page.update()

    save_button.on_click = save_deportista

    form_content = ft.Column(
        [
            ft.Text("Datos básicos", weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            ft.ResponsiveRow([
                ft.Container(content=identi, col={"xs": 12, "sm": 6}),
                ft.Container(content=tipo_identi, col={"xs": 12, "sm": 6}),
            ]),
            ft.ResponsiveRow([ft.Container(content=nombre, col={"xs": 12})]),
            ft.ResponsiveRow([
                ft.Container(content=sexo, col={"xs": 12, "sm": 4}),
                ft.Container(content=fecha_nac, col={"xs": 10, "sm": 5}),
                ft.Container(content=fecha_nac_btn, col={"xs": 2, "sm": 1}),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.ResponsiveRow([
                ft.Container(content=img_preview, col={"xs": 12, "sm": 6}),
                ft.Container(
                    content=ft.Column([photo_button, photo_name], spacing=6),
                    col={"xs": 12, "sm": 6},
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(),
            ft.Text("Ubicación y contacto", weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            ft.Text("Lugar de Nacimiento:", weight="bold", size=13),
            ft.ResponsiveRow([
                ft.Container(content=pais_nac, col={"xs": 12, "sm": 4}),
                ft.Container(content=dep_nac, col={"xs": 12, "sm": 4}),
                ft.Container(content=ciudad_nac, col={"xs": 12, "sm": 4}),
            ]),
            ft.Divider(),
            ft.Text("Residencia y Contacto:", weight="bold", size=13),
            ft.ResponsiveRow([
                ft.Container(content=dep_resi, col={"xs": 12, "sm": 6}),
                ft.Container(content=ciudad_resi, col={"xs": 12, "sm": 6}),
            ]),
            ft.ResponsiveRow([ft.Container(content=direcc_resi, col={"xs": 12})]),
            ft.ResponsiveRow([
                ft.Container(content=telefono, col={"xs": 12, "sm": 6}),
                ft.Container(content=email, col={"xs": 12, "sm": 6}),
            ]),
            ft.Divider(),
            ft.Text("Información socioeconómica", weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            ft.ResponsiveRow([
                ft.Container(content=estrato_dd, col={"xs": 12, "sm": 4}),
                ft.Container(content=nivel_edu_dd, col={"xs": 12, "sm": 4}),
                ft.Container(content=nombre_institu, col={"xs": 12, "sm": 4}),
            ]),
            ft.Divider(),
            ft.ResponsiveRow([ft.Container(content=observaciones, col={"xs": 12})]),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar Deportista"),
        content=ft.Container(
            content=form_content,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dlg()),
            save_button,
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dlg():
        close_control(dlg_modal)

    def open_add_modal(e):
        try:
            clean_form()
            if is_mobile(page):
                show_mobile_form(0)
                return
            size = responsive_dialog_size(page)
            dlg_modal.content.width = size["width"]
            dlg_modal.content.height = size["height"]
            dlg_modal.title.value = "Registrar Deportista"
            dlg_modal.content.content = form_content
            open_control(dlg_modal)
        except Exception as ex:
            print(f"Error opening modal: {ex}")
        
    def open_edit_modal(deportista):
        nonlocal current_edit_id, selected_photo
        current_edit_id = deportista["IDENTI_DEPORTISTA"]
        selected_photo = None
        photo_name.value = "Sin foto nueva seleccionada"
        
        # Populate Basic
        identi.value = deportista["IDENTI_DEPORTISTA"]
        identi.read_only = True 
        tipo_identi.value = str(deportista["TIPO_IDENTI"]) if deportista["TIPO_IDENTI"] else None
        nombre.value = deportista["NOMBRE_DEPORTISTA"]
        sexo.value = deportista["SEXO_DEPORTISTA"]
        fecha_nac.value = deportista["FECHA_NAC"]
        
        # Determine photo placeholder
        img_preview.src = deportista["FOTO_DEPORTISTA"] if deportista["FOTO_DEPORTISTA"] else "https://via.placeholder.com/150"

        # Populate Location
        pais_nac.value = deportista["PAIS_NAC"] or ""
        dep_nac.value = deportista["DEPARTA_NAC"] or ""
        ciudad_nac.value = deportista["CIUDAD_NAC"] or ""
        dep_resi.value = deportista["DEPARTA_RESI"] or ""
        ciudad_resi.value = deportista["CIUDAD_RESI"] or ""
        direcc_resi.value = deportista["DIRECC_RESI"] or ""
        telefono.value = deportista["TELEFONO"] or ""
        email.value = deportista["E_MAIL"] or ""

        # Populate Socio
        estrato_dd.value = str(deportista["ID_ESTRATO"]) if deportista["ID_ESTRATO"] else None
        nivel_edu_dd.value = str(deportista["ID_NIVEL"]) if deportista["ID_NIVEL"] else None
        nombre_institu.value = deportista["NOMBRE_INSTITU"] or ""
        observaciones.value = deportista["OBSERVACIONES"] or ""
        
        size = responsive_dialog_size(page)
        dlg_modal.content.width = size["width"]
        dlg_modal.content.height = size["height"]
        dlg_modal.title.value = "Editar Deportista"
        if is_mobile(page):
            show_mobile_form(0)
        else:
            open_control(dlg_modal)

    # Delete Confirmation Logic
    def delete_deportista(id_deportista):
        try:
            api.delete_deportista(id_deportista)
            show_snack(page, "Deportista eliminado")
            load_deportistas()
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as ex:
             show_snack(page, f"Error de conexion: {ex}")
        page.update()

    def confirm_delete(id_deportista):
        def close_confirm(e):
            close_control(dlg_confirm)
            
        def on_delete(e):
            delete_deportista(id_deportista)
            close_confirm(e)

        dlg_confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar al deportista {id_deportista}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_confirm),
                ft.TextButton("Eliminar", on_click=on_delete, style=ft.ButtonStyle(color="red")),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_control(dlg_confirm)

    # Data Table
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Acciones")),
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Sexo")),
            ft.DataColumn(ft.Text("Edad")),
            ft.DataColumn(ft.Text("Ciudad")),
            ft.DataColumn(ft.Text("Contacto")),
        ],
        rows=[]
    )
    mobile_rows = ft.Column(spacing=8)
    result_text = ft.Text("Cargando deportistas...", color=theme.SUBTITLE_COLOR, size=13)
    empty_state = make_empty_state("No hay deportistas para mostrar")
    empty_state.visible = False
    current_page = 1
    page_size = 10
    total_count = 0
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)

    def update_pagination_controls():
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        pagination_text.value = f"Página {current_page} de {total_pages}"
        prev_button.disabled = current_page <= 1
        next_button.disabled = current_page >= total_pages

    def change_page(delta):
        nonlocal current_page
        current_page = max(1, current_page + delta)
        load_deportistas(search_field.value, current_page)

    prev_button = ft.IconButton(
        ft.Icons.CHEVRON_LEFT,
        icon_color=PRIMARY_COLOR,
        tooltip="Página anterior",
        on_click=lambda e: change_page(-1),
    )
    next_button = ft.IconButton(
        ft.Icons.CHEVRON_RIGHT,
        icon_color=PRIMARY_COLOR,
        tooltip="Página siguiente",
        on_click=lambda e: change_page(1),
    )
    search_button = ft.IconButton(
        ft.Icons.SEARCH,
        icon_color=PRIMARY_COLOR,
        on_click=lambda e: load_deportistas(search_field.value),
    )
    refresh_button = ft.IconButton(
        ft.Icons.REFRESH,
        icon_color=PRIMARY_COLOR,
        tooltip="Actualizar",
        on_click=lambda e: load_deportistas(search_field.value, current_page),
    )
    add_button = ft.ElevatedButton(
        "Agregar Deportista",
        icon=ft.Icons.ADD,
        bgcolor=PRIMARY_COLOR,
        color="white",
        on_click=open_add_modal,
    )

    def set_mobile_shell_visible(visible):
        header = getattr(page, "_somatocarta_mobile_header", None)
        bottom = getattr(page, "_somatocarta_bottom_navigation", None)
        if header is not None:
            header.visible = visible
        if bottom is not None:
            bottom.visible = visible

    def mobile_progress(active_step):
        controls = []
        for index in range(4):
            selected = index == active_step
            completed = index < active_step
            controls.append(
                ft.Container(
                    content=ft.Text(
                        str(index + 1),
                        size=11,
                        color=ft.Colors.WHITE if selected or completed else theme.MUTED_TEXT_COLOR,
                    ),
                    width=24,
                    height=24,
                    border_radius=12,
                    bgcolor=PRIMARY_COLOR if selected or completed else "#e3e8ef",
                    alignment=ft.alignment.center,
                )
            )
            if index < 3:
                controls.append(
                    ft.Container(
                        height=2,
                        bgcolor=PRIMARY_COLOR if index < active_step else "#d8e1ee",
                        expand=True,
                    )
                )
        return ft.Row(controls, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def validate_basic_step():
        message = required_missing(
            [
                (identi, "La identificacion es obligatoria"),
                (tipo_identi, "El tipo de documento es obligatorio"),
                (nombre, "El nombre es obligatorio"),
                (sexo, "El sexo es obligatorio"),
            ]
        )
        if message:
            show_snack(page, message)
            return False
        return True

    def mobile_step_body(step):
        if step == 0:
            return "Datos básicos", [
                tipo_identi,
                identi,
                nombre,
                sexo,
                ft.Row([fecha_nac, fecha_nac_btn], spacing=4),
            ]
        if step == 1:
            return "Contacto y ubicación", [
                telefono,
                email,
                ft.Text("Lugar de nacimiento", size=12, weight=ft.FontWeight.BOLD, color=theme.MUTED_TEXT_COLOR),
                pais_nac,
                dep_nac,
                ciudad_nac,
                ft.Text("Residencia", size=12, weight=ft.FontWeight.BOLD, color=theme.MUTED_TEXT_COLOR),
                dep_resi,
                ciudad_resi,
                direcc_resi,
            ]
        if step == 2:
            return "Información socioeconómica", [
                estrato_dd,
                nivel_edu_dd,
                nombre_institu,
                observaciones,
            ]

        photo_preview = ft.Stack(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, size=70, color="#6b7280"),
                    width=198,
                    height=198,
                    bgcolor="#d1d5db",
                    border_radius=99,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=img_preview,
                    width=198,
                    height=198,
                    border_radius=99,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.ADD_A_PHOTO,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Seleccionar foto",
                        on_click=pick_photo,
                    ),
                    width=54,
                    height=54,
                    left=150,
                    top=150,
                    bgcolor=PRIMARY_COLOR,
                    border_radius=27,
                    alignment=ft.alignment.center,
                ),
            ],
            width=204,
            height=204,
        )
        img_preview.width = 198
        img_preview.height = 198
        img_preview.fit = ft.ImageFit.COVER
        return "Foto del deportista", [
            ft.Container(photo_preview, alignment=ft.alignment.center, padding=ft.padding.only(top=28)),
            ft.Container(photo_name, alignment=ft.alignment.center),
        ]

    def show_mobile_form(step):
        nonlocal mobile_step
        if step > mobile_step and mobile_step == 0 and not validate_basic_step():
            return
        mobile_step = max(0, min(step, 3))
        set_mobile_shell_visible(False)
        def handle_system_back():
            if mobile_step == 0:
                show_mobile_list()
            else:
                show_mobile_form(mobile_step - 1)
            return True

        page._somatocarta_local_back_handler = handle_system_back
        section, fields = mobile_step_body(mobile_step)

        def go_previous(_):
            if mobile_step == 0:
                show_mobile_list()
            else:
                show_mobile_form(mobile_step - 1)

        title = "Editar deportista" if current_edit_id else "Nuevo deportista"
        trailing = []
        if current_edit_id:
            trailing.append(
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=theme.ERROR_COLOR,
                    tooltip="Eliminar deportista",
                    on_click=lambda _: confirm_delete(current_edit_id),
                )
            )
        mobile_form_header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_previous, icon_color=theme.INK_COLOR),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme.INK_COLOR, expand=True),
                    *trailing,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=64,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, theme.SURFACE_BORDER)),
            padding=ft.padding.only(right=8),
        )
        action_controls = []
        if mobile_step > 0:
            action_controls.append(
                ft.OutlinedButton(
                    "Anterior",
                    on_click=lambda _: show_mobile_form(mobile_step - 1),
                    height=44,
                    expand=True,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                )
            )
        action_controls.append(
            ft.ElevatedButton(
                "Guardar" if mobile_step == 3 else "Siguiente",
                icon=ft.Icons.SAVE_OUTLINED if mobile_step == 3 else None,
                on_click=save_deportista if mobile_step == 3 else lambda _: show_mobile_form(mobile_step + 1),
                height=44,
                expand=True,
                bgcolor=theme.SUCCESS_COLOR if mobile_step == 3 else PRIMARY_COLOR,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), elevation=0),
            )
        )
        body = ft.Column(
            [
                mobile_progress(mobile_step),
                ft.Text(section, size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                *fields,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )
        mobile_root.content = ft.Column(
            [
                mobile_form_header,
                mobile_screen(
                    body,
                    bottom_action=ft.Row(action_controls, spacing=14),
                ),
            ],
            spacing=0,
            expand=True,
        )
        page.update()

    def show_mobile_list():
        set_mobile_shell_visible(True)
        page._somatocarta_local_back_handler = None
        mobile_search = mobile_search_field(
            "Buscar deportista...",
            value=search_field.value,
            on_search=lambda query: load_deportistas(query, 1),
        )
        mobile_search.expand = True
        pagination = ft.Row(
            [prev_button, pagination_text, next_button],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=total_count > page_size,
        )
        mobile_root.content = mobile_screen(
            ft.Column(
                [
                    mobile_search,
                    mobile_primary_button("Nuevo deportista", on_click=open_add_modal),
                    mobile_rows,
                    empty_state,
                    pagination,
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
        )
        page.update()

    def load_deportistas(search_query="", requested_page=1):
        nonlocal current_page, total_count
        current_page = max(1, requested_page)
        controls = [search_button, refresh_button, prev_button, next_button, add_button]
        set_busy(page, controls, True, result_text, "Cargando deportistas...")
        try:
            page_data = api.list_deportistas_page(search_query, current_page, page_size)
            data = page_data["items"]
            total_count = page_data["total"]
            table.rows = []
            mobile_rows.controls.clear()
            empty_state.visible = not data
            result_text.value = f"{len(data)} de {total_count} deportistas"
            for d in data:
                table.rows.append(build_deportista_row(d, open_edit_modal, confirm_delete))
                mobile_rows.controls.append(
                    mobile_list_card(
                        d.get("NOMBRE_DEPORTISTA") or "-",
                        f"ID: {d.get('IDENTI_DEPORTISTA') or '-'}",
                        d.get("NOMBRE_DEPORTISTA") or "",
                        "#dbeafe",
                        on_click=lambda e, item=d: open_edit_modal(item),
                    )
                )
            update_pagination_controls()
            page.update()
        except ApiError as error:
            table.rows = []
            mobile_rows.controls.clear()
            empty_state.visible = True
            result_text.value = "No se pudo cargar la lista"
            total_count = 0
            update_pagination_controls()
            show_snack(page, str(error))
            page.update()
        except Exception as error:
            table.rows = []
            mobile_rows.controls.clear()
            empty_state.visible = True
            result_text.value = "No se pudo cargar la lista"
            total_count = 0
            update_pagination_controls()
            show_snack(page, f"Error de conexion: {error}")
            page.update()
        finally:
            update_pagination_controls()
            for control in controls:
                control.disabled = False
            update_pagination_controls()
            page.update()

    load_deportistas()

    def go_back(e):
        show_dashboard(page)

    if is_mobile(page):
        show_mobile_list()
        return mobile_root

    return ft.Container(
        content=ft.Column(
            [
                page_header("Deportistas", on_back=go_back, color=TEXT_COLOR),
                ft.Container(height=16),
                ft.ResponsiveRow(
                    [
                        ft.Container(content=search_field, col={"xs": 8, "sm": 8, "md": 6, "lg": 5}),
                        ft.Container(content=search_button, col={"xs": 2, "sm": 2, "md": 1}),
                        ft.Container(content=refresh_button, col={"xs": 2, "sm": 2, "md": 1}),
                        ft.Container(
                            content=add_button,
                            col={"xs": 12, "sm": 12, "md": 4, "lg": 5},
                            alignment=ft.alignment.center_right if (page.width or 1024) >= 768 else ft.alignment.center,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    run_spacing=10,
                ),
                ft.Container(height=16),
                content_card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Listado", weight="bold", color=TEXT_COLOR, size=15),
                                    result_text,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(),
                            ft.Row(
                                [table],
                                scroll=ft.ScrollMode.ALWAYS,
                            ),
                            empty_state,
                            ft.Row(
                                [
                                    prev_button,
                                    pagination_text,
                                    next_button,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ]
                    )
                )
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=responsive_padding(page),
        bgcolor=BG_COLOR,
        expand=True
    )
