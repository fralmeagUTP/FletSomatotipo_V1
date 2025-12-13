import flet as ft
import requests
from datetime import datetime
import os

API_URL = "http://127.0.0.1:8085"

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
    PRIMARY_COLOR = "#2e5cb8"
    BG_COLOR = "#f5f7fb"
    CARD_BG = ft.Colors.WHITE
    TEXT_COLOR = "#333333"

    # State
    current_edit_id = None 
    selected_file_path = None # Store selected file path locally

    # Catalogs
    tipos_documentos = []
    estratos = []
    niveles_educativos = []

    def load_catalogs():
        nonlocal tipos_documentos, estratos, niveles_educativos
        try:
            tipos_documentos = requests.get(f"{API_URL}/catalogos/tipos_documento").json()
            estratos = requests.get(f"{API_URL}/catalogos/estratos").json()
            niveles_educativos = requests.get(f"{API_URL}/catalogos/niveles_educativos").json()
        except Exception as e:
            print(f"Error loading catalogs: {e}")

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
        last_date=datetime.now(),
    )
    
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    fecha_nac_btn = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: date_picker.pick_date(),
    )
    
    # Photo Upload Logic
    img_preview = ft.Image(
        src="https://via.placeholder.com/150", # Default placeholder
        width=150,
        height=150,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10)
    )
    
    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal selected_file_path
        if e.files:
            file_path = e.files[0].path
            selected_file_path = file_path
            img_preview.src = file_path # Show local preview
            img_preview.update()
            
    file_picker = ft.FilePicker(on_result=on_file_picked)
    if file_picker not in page.overlay:
        page.overlay.append(file_picker)
        
    btn_upload_photo = ft.ElevatedButton(
        "Seleccionar Foto",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
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


    search_field = ft.TextField(
        label="Buscar por nombre o ID", 
        suffix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: load_deportistas(e.control.value)
    )

    def clean_form():
        nonlocal current_edit_id, selected_file_path
        current_edit_id = None
        selected_file_path = None
        identi.value = ""
        identi.read_only = False
        tipo_identi.value = None
        nombre.value = ""
        sexo.value = None
        fecha_nac.value = ""
        img_preview.src = "https://via.placeholder.com/150"
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

    def upload_photo(file_path):
        try:
            url = f"{API_URL}/files/upload"
            with open(file_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(url, files=files)
                if resp.status_code == 200:
                    return f"{API_URL}{resp.json()['url']}"
        except Exception as e:
            print(f"Error uploading file: {e}")
        return None

    def save_deportista(e):
        # 1. Upload photo if selected
        final_photo_url = img_preview.src
        if selected_file_path:
            uploaded_url = upload_photo(selected_file_path)
            if uploaded_url:
                final_photo_url = uploaded_url

        data = {
            "IDENTI_DEPORTISTA": identi.value,
            "TIPO_IDENTI": int(tipo_identi.value) if tipo_identi.value else 0,
            "NOMBRE_DEPORTISTA": nombre.value,
            "SEXO_DEPORTISTA": sexo.value,
            "FECHA_NAC": fecha_nac.value if fecha_nac.value else None,
            "FOTO_DEPORTISTA": final_photo_url,
            "PAIS_NAC": pais_nac.value,
            "DEPARTA_NAC": dep_nac.value,
            "CIUDAD_NAC": ciudad_nac.value,
            "DEPARTA_RESI": dep_resi.value,
            "CIUDAD_RESI": ciudad_resi.value,
            "DIRECC_RESI": direcc_resi.value,
            "TELEFONO": telefono.value,
            "E_MAIL": email.value,
            "ID_ESTRATO": int(estrato_dd.value) if estrato_dd.value else None,
            "ID_NIVEL": int(nivel_edu_dd.value) if nivel_edu_dd.value else None,
            "NOMBRE_INSTITU": nombre_institu.value,
            "OBSERVACIONES": observaciones.value
        }

        try:
            if current_edit_id:
                # Update
                resp = requests.put(f"{API_URL}/deportistas/{current_edit_id}", json=data)
            else:
                # Create
                resp = requests.post(f"{API_URL}/deportistas/", json=data)

            if resp.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Deportista guardado exitosamente"))
                page.snack_bar.open = True
                clean_form()
                page.close(dlg_modal)
                load_deportistas() 
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {resp.text}"))
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"))
            page.snack_bar.open = True
        page.update()

    # Modal for Add/Edit using Tabs for organization
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Datos Básicos",
                content=ft.Column([
                    ft.Container(height=10),
                    ft.ResponsiveRow([
                        ft.Container(content=identi, col={"xs": 12, "md": 6}),
                        ft.Container(content=tipo_identi, col={"xs": 12, "md": 6})
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(content=nombre, col={"xs": 12})
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(content=sexo, col={"xs": 12, "sm": 5}),
                        ft.Container(content=fecha_nac, col={"xs": 10, "sm": 5}),
                        ft.Container(content=fecha_nac_btn, col={"xs": 2, "sm": 2})
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.ResponsiveRow([
                        ft.Container(content=img_preview, col={"xs": 12, "md": 6}), 
                        ft.Container(content=btn_upload_photo, col={"xs": 12, "md": 6})
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], spacing=10)
            ),
            ft.Tab(
                text="Ubicación y Contacto",
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Text("Lugar de Nacimiento:", weight="bold"),
                    ft.ResponsiveRow([
                        ft.Container(content=pais_nac, col={"xs": 12, "md": 6}),
                        ft.Container(content=dep_nac, col={"xs": 12, "md": 6})
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(content=ciudad_nac, col={"xs": 12, "md": 6})
                    ]),
                    ft.Divider(),
                    ft.Text("Residencia y Contacto:", weight="bold"),
                    ft.ResponsiveRow([
                         ft.Container(content=dep_resi, col={"xs": 12, "md": 6}),
                         ft.Container(content=ciudad_resi, col={"xs": 12, "md": 6})
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(content=direcc_resi, col={"xs": 12})
                    ]),
                    ft.ResponsiveRow([
                         ft.Container(content=telefono, col={"xs": 12, "md": 6}),
                         ft.Container(content=email, col={"xs": 12, "md": 6})
                    ])
                ], spacing=10)
            ),
            ft.Tab(
                text="Socio-Económico",
                content=ft.Column([
                    ft.Container(height=10),
                    ft.ResponsiveRow([
                        ft.Container(content=estrato_dd, col={"xs": 12, "md": 4}),
                        ft.Container(content=nivel_edu_dd, col={"xs": 12, "md": 8})
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(content=nombre_institu, col={"xs": 12})
                    ]),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(content=observaciones, col={"xs": 12})
                    ])
                ], spacing=10)
            ),
        ],
        expand=1,
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar Deportista"),
        content=ft.Container(
            content=tabs,
            width=650,
            height=600, # Increased height for photo
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dlg()),
            ft.ElevatedButton("Guardar", on_click=save_deportista),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dlg():
        page.close(dlg_modal)

    def open_add_modal(e):
        print("Opening add modal...")
        try:
            clean_form()
            dlg_modal.title.value = "Registrar Deportista"
            page.open(dlg_modal)
        except Exception as ex:
            print(f"Error opening modal: {ex}")
        
    def open_edit_modal(deportista):
        nonlocal current_edit_id, selected_file_path
        current_edit_id = deportista["IDENTI_DEPORTISTA"]
        selected_file_path = None # Reset new file selection
        
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
        
        dlg_modal.title.value = "Editar Deportista"
        page.open(dlg_modal)

    # Delete Confirmation Logic
    def delete_deportista(id_deportista):
        try:
            resp = requests.delete(f"{API_URL}/deportistas/{id_deportista}")
            if resp.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Deportista eliminado"))
                page.snack_bar.open = True
                load_deportistas()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {resp.text}"))
                page.snack_bar.open = True
        except Exception as ex:
             page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"))
             page.snack_bar.open = True
        page.update()

    def confirm_delete(id_deportista):
        def close_confirm(e):
            page.close(dlg_confirm)
            
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
        page.open(dlg_confirm)

    # Data Table
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Sexo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def load_deportistas(search_query=""):
        try:
            params = {}
            if search_query:
                params["search"] = search_query
                
            resp = requests.get(f"{API_URL}/deportistas/", params=params)
            
            if resp.status_code == 200:
                data = resp.json()
                table.rows = []
                for d in data:
                    id_d = d["IDENTI_DEPORTISTA"]
                    table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(d["IDENTI_DEPORTISTA"]))),
                                ft.DataCell(ft.Text(d["NOMBRE_DEPORTISTA"])),
                                ft.DataCell(ft.Text(d["SEXO_DEPORTISTA"])),
                                ft.DataCell(
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                ft.Icons.EDIT, 
                                                icon_color=PRIMARY_COLOR,
                                                on_click=lambda e, dept=d: open_edit_modal(dept)
                                            ),
                                            ft.IconButton(
                                                ft.Icons.DELETE, 
                                                icon_color="red",
                                                on_click=lambda e, i=id_d: confirm_delete(i)
                                            ),
                                        ]
                                    )
                                ),
                            ]
                        )
                    )
                page.update()
        except Exception as e:
            print(f"Error loading deportistas: {e}")

    load_deportistas()

    def go_back(e):
        from .dashboard import DashboardView
        page.clean()
        page.add(DashboardView(page))

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back, icon_color=TEXT_COLOR),
                        ft.Text("Deportistas", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=20),
                ft.ResponsiveRow(
                    [
                        ft.Container(content=search_field, col={"xs": 12, "md": 6, "lg": 4}),
                        ft.Container(content=ft.IconButton(ft.Icons.SEARCH, icon_color=PRIMARY_COLOR, on_click=lambda e: load_deportistas(search_field.value)), col={"xs": 2, "md": 1}),
                        # Spacer or just alignment? RRow fits.
                        # ft.Container(expand=True), # ResponsiveRow doesn't use expand like Row.
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Agregar Deportista", 
                                icon=ft.Icons.ADD, 
                                bgcolor=PRIMARY_COLOR, 
                                color="white",
                                on_click=open_add_modal,
                                width=200 # Fixed width for button is okay, or make it expand
                            ),
                            col={"xs": 12, "md": 4},
                            alignment=ft.alignment.center_right
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=20),
                ft.Container(
                    content=table,
                    bgcolor=CARD_BG,
                    border_radius=10,
                    padding=10,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLUE_GREY_50)
                )
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=40,
        bgcolor=BG_COLOR,
        expand=True
    )
