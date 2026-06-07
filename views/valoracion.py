import flet as ft
from datetime import datetime
from app_config import show_snack
from src.frontend.components import inline_status, page_header, section_title
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.form_helpers import build_measurement_detail, build_somatotipo_payload
from src.frontend.navigation import show_dashboard
from src.frontend.table_builders import build_measurement_row
from src.frontend import theme

def ValoracionView(page: ft.Page):
    """
    Vista de Valoración Corporal (Somatotipo).
    Permite registrar mediciones antropométricas.
    """
    # Colors
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    BG_COLOR = theme.BACKGROUND_COLOR
    CARD_BG = theme.CARD_BACKGROUND
    TEXT_COLOR = theme.TEXT_COLOR
    SUCCESS_COLOR = ft.Colors.GREEN_700
    MUTED_COLOR = theme.SUBTITLE_COLOR

    # State
    selected_athlete_id = None
    added_details_list = [] # List to store local details
    api = ApiClient(page)
    
    details_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Peso")),
            ft.DataColumn(ft.Text("Estatura")),
            ft.DataColumn(ft.Text("Pliegues (mm)")), # Summary
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )
    progress_text = ft.Text("1. Selecciona deportista  |  2. Captura medidas  |  3. Guarda valoración", color=MUTED_COLOR, size=13)
    summary_text = ft.Text("Sin mediciones agregadas", color=MUTED_COLOR, size=13)
    empty_measurements = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY_COLOR, size=20),
                ft.Text("Agrega una medición para revisar el resumen antes de guardar.", color=MUTED_COLOR),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=12,
        visible=True,
    )
    
    # --- Components ---
    
    # 1. Athlete Selection
    athlete_search = ft.TextField(
        label="Buscar Deportista (ID o Nombre)", 
        suffix=ft.IconButton(ft.Icons.SEARCH, on_click=lambda e: search_athlete(athlete_search.value)),
        on_submit=lambda e: search_athlete(e.control.value)
    )
    
    athlete_info_text = ft.Text("Ningún deportista seleccionado", color="red") # Restored

    # Athlete Info Containers
    info_nombre = ft.Text("-", weight="bold", size=16)
    info_edad = ft.Text("-")
    info_ciudad = ft.Text("-")
    info_institucion = ft.Text("-")
    info_email = ft.Text("-")

    athlete_info_container = ft.Column([
        ft.Row([ft.Text("Nombre:", weight="bold"), info_nombre]),
        ft.Row([ft.Text("Edad:", weight="bold"), info_edad]),
        ft.Row([ft.Text("Ciudad:", weight="bold"), info_ciudad, ft.Text(" | Institución:", weight="bold"), info_institucion]),
        ft.Row([ft.Text("Email:", weight="bold"), info_email]),
    ], spacing=2, visible=False)

    def calculate_age(birth_date_str, measure_date_str):
        if not birth_date_str:
            return "Sin fecha nacimiento"
        try:
            birth = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            measure = datetime.strptime(measure_date_str, '%Y-%m-%d').date()
            age = measure.year - birth.year - ((measure.month, measure.day) < (birth.month, birth.day))
            return f"{age} años"
        except Exception as e:
            return "Error Calc."

    def search_athlete(query):
        nonlocal selected_athlete_id
        if not query:
            return
        
        try:
            data = api.list_deportistas(query)
            if data:
                # Select the first match
                first_match = data[0]
                selected_athlete_id = first_match["IDENTI_DEPORTISTA"]

                # Update Info
                info_nombre.value = f"{first_match['NOMBRE_DEPORTISTA']} ({selected_athlete_id})"

                # Age Calc
                fecha_nac = first_match.get("FECHA_NAC")
                info_edad.value = calculate_age(fecha_nac, fecha_medida.value)

                # Other Info
                info_ciudad.value = first_match.get("CIUDAD_RESI") or "N/A"
                info_institucion.value = first_match.get("NOMBRE_INSTITU") or "N/A"
                info_email.value = first_match.get("E_MAIL") or "N/A"

                athlete_info_container.visible = True
                athlete_info_text.visible = False # Hide the old simple text
                update_progress()
            else:
                selected_athlete_id = None
                athlete_info_text.value = "No se encontraron deportistas."
                athlete_info_text.color = "red"
                athlete_info_text.visible = True
                athlete_info_container.visible = False
                update_progress()
        except ApiError as error:
            show_snack(page, str(error))
            athlete_info_text.value = "Error al buscar."
            athlete_info_text.visible = True
        except Exception as e:
            athlete_info_text.value = f"Error: {e}"
            athlete_info_text.visible = True
        page.update()

    # 2. Date
    fecha_medida = ft.TextField(
        label="Fecha Medición", 
        value=datetime.now().strftime('%Y-%m-%d'),
        read_only=True
    )
    
    # 3. Observaciones
    observaciones = ft.TextField(label="Observaciones", multiline=True)

    # 4. Measurements Fields
    # Helper to create numeric fields
    def num_field(label, suffix=""):
        return ft.TextField(
            label=label, 
            suffix_text=suffix, 
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT
        )

    # Basic
    estatura = num_field("Estatura", "cm")
    peso = num_field("Peso", "kg")

    # Pliegues
    p_tricipital = num_field("Tricipital", "mm")
    p_subescapular = num_field("Subescapular", "mm")
    p_suprailiaco = num_field("Suprailiaco", "mm")
    p_abdominal = num_field("Abdominal", "mm")
    p_muslo = num_field("Muslo Anterior", "mm")
    p_pierna = num_field("Pierna Medial", "mm")

    # Diameters
    d_muneca = num_field("Biepicondilar Muñeca", "mm") # Hueso
    d_femur = num_field("Biepicondilar Fémur", "mm")
    d_codo = num_field("Codo", "mm") # Usually implied by humerus/femur but listed in model
    c_carpo = num_field("Circunferencia Carpo", "mm")

    # Perimeters
    perim_bicep = num_field("Bíceps Contraído", "cm")
    perim_pierna = num_field("Pierna", "cm")

    measurement_fields = {
        "estatura": estatura,
        "peso": peso,
        "p_tricipital": p_tricipital,
        "p_subescapular": p_subescapular,
        "p_suprailiaco": p_suprailiaco,
        "p_abdominal": p_abdominal,
        "p_muslo": p_muslo,
        "p_pierna": p_pierna,
        "d_muneca": d_muneca,
        "d_femur": d_femur,
        "d_codo": d_codo,
        "c_carpo": c_carpo,
        "perim_bicep": perim_bicep,
        "perim_pierna": perim_pierna,
    }

    def update_progress():
        if selected_athlete_id and added_details_list:
            progress_text.value = "1. Deportista seleccionado  |  2. Medidas listas  |  3. Pendiente guardar"
            progress_text.color = SUCCESS_COLOR
        elif selected_athlete_id:
            progress_text.value = "1. Deportista seleccionado  |  2. Captura medidas  |  3. Guarda valoración"
            progress_text.color = PRIMARY_COLOR
        else:
            progress_text.value = "1. Selecciona deportista  |  2. Captura medidas  |  3. Guarda valoración"
            progress_text.color = MUTED_COLOR

    def render_measurements():
        details_table.rows.clear()
        empty_measurements.visible = not added_details_list
        if not added_details_list:
            summary_text.value = "Sin mediciones agregadas"
        else:
            last = added_details_list[-1]
            summary_text.value = (
                f"{len(added_details_list)} medicion(es) agregada(s). "
                f"Ultima: {last['PESO_kg']} kg, {last['ESTA_USER_CM']} cm"
            )
        for detail in added_details_list:
            details_table.rows.append(build_measurement_row(detail, remove_medicion))
        update_progress()

    def add_medicion(e):
        try:
            det = build_measurement_detail(measurement_fields)
            
            added_details_list.append(det)
            render_measurements()
            
            # Clear fields (Optional, but good UX)
            # estatura.value = "" 
            # peso.value = ""
            # ... clear others ...
            
            show_snack(page, "Medición agregada a la lista")
            page.update()

        except ValueError as ex:
            show_snack(page, str(ex))
            page.update()

    def remove_medicion(det):
        if det in added_details_list:
            added_details_list.remove(det)
            render_measurements()
            page.update()


    def save_valoracion(e):
        if not selected_athlete_id:
            show_snack(page, "Debe seleccionar un deportista primero")
            page.update()
            return

        current_user = page.session.get("login_user")
        if not current_user:
             show_snack(page, "Sesion expirada. Inicia sesion nuevamente.")
             page.update()
             return

        if not added_details_list:
             show_snack(page, "Debe agregar al menos una medición a la lista")
             page.update()
             return

        try:
            payload = build_somatotipo_payload(
                selected_athlete_id,
                current_user,
                fecha_medida.value,
                observaciones.value,
                added_details_list,
            )

            api.create_somatotipo(payload)
            show_snack(page, "Valoración guardada exitosamente")
            page.update()
            # Redirect to Dashboard
            import time
            time.sleep(1) # Brief delay to see the message
            go_back(e)
            
        except ValueError:
            show_snack(page, "Por favor verifique que todos los campos numéricos sean válidos")
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as ex:
            show_snack(page, f"Error de conexión: {ex}")
        
        page.update()

    def go_back(e):
        show_dashboard(page)

    # Layout
    return ft.Container(
        content=ft.Column(
            [
                # Header
                page_header("Valoración Corporal", on_back=go_back, color=TEXT_COLOR),
                ft.Container(height=20),
                
                # Card Container
                ft.Container(
                    content=ft.Column(
                        [
                            inline_status(progress_text, icon=ft.Icons.TASK_ALT),
                            section_title("Datos del Deportista"),
                            ft.ResponsiveRow([
                                ft.Container(content=athlete_search, col={"xs": 12, "md": 5}),
                                ft.Container(content=ft.Column([athlete_info_text, athlete_info_container]), col={"xs": 12, "md": 7}, alignment=ft.alignment.center_left),
                            ], vertical_alignment=ft.CrossAxisAlignment.START),
                            
                            ft.Divider(),
                            
                            section_title("Datos Básicos"),
                            ft.ResponsiveRow([
                                ft.Container(content=fecha_medida, col={"xs": 12, "sm": 6, "md": 4}),
                                ft.Container(content=estatura, col={"xs": 6, "sm": 3, "md": 4}),
                                ft.Container(content=peso, col={"xs": 6, "sm": 3, "md": 4}),
                            ]),

                            ft.Divider(),
                            
                            section_title("Pliegues Cutáneos (mm)"),
                            ft.ResponsiveRow([
                                ft.Container(content=p_tricipital, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_subescapular, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_suprailiaco, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_abdominal, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_muslo, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_pierna, col={"xs": 6, "md": 4}),
                            ]),

                            ft.Divider(),

                            section_title("Diámetros y Perímetros"),
                            ft.ResponsiveRow([
                                ft.Container(content=d_muneca, col={"xs": 6, "md": 3}),
                                ft.Container(content=d_femur, col={"xs": 6, "md": 3}),
                                ft.Container(content=d_codo, col={"xs": 6, "md": 3}),
                                ft.Container(content=c_carpo, col={"xs": 6, "md": 3}),
                                ft.Container(content=perim_bicep, col={"xs": 6, "md": 6}),
                                ft.Container(content=perim_pierna, col={"xs": 6, "md": 6}),
                            ]),
                            
                            ft.Divider(),
                            
                            ft.ResponsiveRow([
                                ft.Container(content=observaciones, col={"xs": 12}),
                            ]),
                            
                            ft.Container(height=10),
                            ft.Divider(),
                            
                            # Add Measurement Button
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "Agregar Medición a la Lista",
                                    icon=ft.Icons.ADD_CHART,
                                    on_click=add_medicion,
                                    bgcolor=ft.Colors.GREEN_600,
                                    color="white"
                                ),
                                alignment=ft.alignment.center_right
                            ),
                            
                            ft.Text("Lista de Mediciones a Guardar:", weight="bold"),
                            summary_text,
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [details_table],
                                            scroll=ft.ScrollMode.ALWAYS
                                        ),
                                        empty_measurements,
                                    ]
                                ),
                                border=ft.border.all(1, "#eeeeee"),
                                border_radius=10
                            ),
                            
                            ft.Container(height=20),
                            
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "Guardar Valoración",
                                    icon=ft.Icons.SAVE,
                                    style=ft.ButtonStyle(
                                        bgcolor=PRIMARY_COLOR,
                                        color="white",
                                        padding=20
                                    ),
                                    on_click=save_valoracion,
                                    width=200
                                ),
                                alignment=ft.alignment.center_right
                            )

                        ],
                        spacing=15
                    ),
                    bgcolor=CARD_BG,
                    padding=30,
                    border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLUE_GREY_50)
                )
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=20,
        bgcolor=BG_COLOR,
        expand=True
    )
