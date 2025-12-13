import flet as ft
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8085"

def ValoracionView(page: ft.Page):
    """
    Vista de Valoración Corporal (Somatotipo).
    Permite registrar mediciones antropométricas.
    """
    # Colors
    PRIMARY_COLOR = "#2e5cb8"
    BG_COLOR = "#f5f7fb"
    CARD_BG = ft.Colors.WHITE
    TEXT_COLOR = "#333333"

    # State
    selected_athlete_id = None
    added_details_list = [] # List to store local details
    
    details_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Peso")),
            ft.DataColumn(ft.Text("Estatura")),
            ft.DataColumn(ft.Text("Pliegues (mm)")), # Summary
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )
    
    # --- Components ---
    
    # 1. Athlete Selection
    athlete_search = ft.TextField(
        label="Buscar Deportista (ID o Nombre)", 
        suffix=ft.IconButton(ft.Icons.SEARCH, on_click=lambda e: search_athlete(athlete_search.value)),
        on_submit=lambda e: search_athlete(e.control.value)
    )
    
    athlete_info_text = ft.Text("Ningún deportista seleccionado", color="red")

    def search_athlete(query):
        nonlocal selected_athlete_id
        if not query:
            return
        
        try:
            # Simple search logic: Get all and filter locally or use backend search if available
            # Ideally backend should support search. using same endpoint as deportistas view
            resp = requests.get(f"{API_URL}/deportistas/", params={"search": query})
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    # Select the first match for simplicity or show a dialog (simplified here to first match)
                    first_match = data[0]
                    selected_athlete_id = first_match["IDENTI_DEPORTISTA"]
                    athlete_info_text.value = f"Seleccionado: {first_match['NOMBRE_DEPORTISTA']} ({selected_athlete_id})"
                    athlete_info_text.color = "green"
                else:
                    selected_athlete_id = None
                    athlete_info_text.value = "No se encontraron deportistas."
                    athlete_info_text.color = "red"
            else:
                athlete_info_text.value = "Error al buscar."
        except Exception as e:
            athlete_info_text.value = f"Error: {e}"
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

    def add_medicion(e):
        try:
            # Validate numeric fields
            det = {
                "ESTA_USER_CM": float(estatura.value or 0),
                "PESO_kg": float(peso.value or 0),
                "PLIEGUE_TRICIPITAL": float(p_tricipital.value or 0),
                "PLIEGUE_SUBESCAPULAR": float(p_subescapular.value or 0),
                "PLIEGUE_SUPRAILIACO": float(p_suprailiaco.value or 0),
                "PLIEGUE_ABDOMINAL": float(p_abdominal.value or 0),
                "PLIEGUE_MUSLO_ANT": float(p_muslo.value or 0),
                "PLIEGUE_MEDIAL_PIERNA": float(p_pierna.value or 0),
                "DIAMETRO_BIEPI_MUNECA": float(d_muneca.value or 0),
                "DIAMETRO_BIEPI_FEMUR": float(d_femur.value or 0),
                "DIAMETRO_CODO": float(d_codo.value or 0),
                "PERIMETRO_BICED_CONTRAIDO": float(perim_bicep.value or 0),
                "PERIMETRO_PIERNA": float(perim_pierna.value or 0),
                "CIRCUNFERENCIA_CARPO": float(c_carpo.value or 0)
            }
            
            # Add to list
            added_details_list.append(det)
            
            # Update Table
            details_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(det["PESO_kg"]))),
                        ft.DataCell(ft.Text(str(det["ESTA_USER_CM"]))),
                        ft.DataCell(ft.Text(f"Tri:{det['PLIEGUE_TRICIPITAL']} Sub:{det['PLIEGUE_SUBESCAPULAR']}...")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.DELETE, 
                                icon_color="red", 
                                on_click=lambda e: remove_medicion(det)
                            )
                        ),
                    ]
                )
            )
            
            # Clear fields (Optional, but good UX)
            # estatura.value = "" 
            # peso.value = ""
            # ... clear others ...
            
            page.snack_bar = ft.SnackBar(ft.Text("Medición agregada a la lista"))
            page.snack_bar.open = True
            page.update()

        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor verifique que todos los campos numéricos sean válidos"))
            page.snack_bar.open = True
            page.update()

    def remove_medicion(det):
        if det in added_details_list:
            added_details_list.remove(det)
            # Rebuild rows to keep index sync simple or just clear/repopulate
            details_table.rows.clear()
            for d in added_details_list:
                 details_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(d["PESO_kg"]))),
                            ft.DataCell(ft.Text(str(d["ESTA_USER_CM"]))),
                            ft.DataCell(ft.Text(f"Tri:{d['PLIEGUE_TRICIPITAL']} Sub:{d['PLIEGUE_SUBESCAPULAR']}...")),
                            ft.DataCell(
                                ft.IconButton(
                                    ft.Icons.DELETE, 
                                    icon_color="red", 
                                    on_click=lambda e, item=d: remove_medicion(item)
                                )
                            ),
                        ]
                    )
                )
            page.update()


    def save_valoracion(e):
        if not selected_athlete_id:
            page.snack_bar = ft.SnackBar(ft.Text("Debe seleccionar un deportista primero"))
            page.snack_bar.open = True
            page.update()
            return

        current_user = page.session.get("username")
        if not current_user:
             # Fallback if session lost or dev mode
             current_user = "admin" 

        if not added_details_list:
             page.snack_bar = ft.SnackBar(ft.Text("Debe agregar al menos una medición a la lista"))
             page.snack_bar.open = True
             page.update()
             return

        try:
            payload = {
                "IDENTI_DEPORTISTA": selected_athlete_id,
                "LOGIN_USER": current_user,
                "FECHA_MEDIDA": fecha_medida.value,
                "OBSERV": observaciones.value,
                "DETALLES": added_details_list
            }

            resp = requests.post(f"{API_URL}/somatotipo/", json=payload)
            
            if resp.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Valoración guardada exitosamente!"))
                page.snack_bar.open = True
                # Clean fields?
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {resp.text}"))
                page.snack_bar.open = True
            
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor verifique que todos los campos numéricos sean válidos"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"))
            page.snack_bar.open = True
        
        page.update()

    def go_back(e):
        from .dashboard import DashboardView
        page.clean()
        page.add(DashboardView(page))

    # Layout
    return ft.Container(
        content=ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back, icon_color=TEXT_COLOR),
                        ft.Text("Valoración Corporal", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=20),
                
                # Card Container
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Datos del Deportista", size=18, weight="bold", color=PRIMARY_COLOR),
                            ft.ResponsiveRow([
                                ft.Container(content=athlete_search, col={"xs": 12, "md": 6}),
                                ft.Container(content=athlete_info_text, col={"xs": 12, "md": 6}, alignment=ft.alignment.center_left),
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            
                            ft.Divider(),
                            
                            ft.Text("Datos Básicos", size=18, weight="bold", color=PRIMARY_COLOR),
                            ft.ResponsiveRow([
                                ft.Container(content=fecha_medida, col={"xs": 12, "sm": 6, "md": 4}),
                                ft.Container(content=estatura, col={"xs": 6, "sm": 3, "md": 4}),
                                ft.Container(content=peso, col={"xs": 6, "sm": 3, "md": 4}),
                            ]),

                            ft.Divider(),
                            
                            ft.Text("Pliegues Cutáneos (mm)", size=18, weight="bold", color=PRIMARY_COLOR),
                            ft.ResponsiveRow([
                                ft.Container(content=p_tricipital, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_subescapular, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_suprailiaco, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_abdominal, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_muslo, col={"xs": 6, "md": 4}),
                                ft.Container(content=p_pierna, col={"xs": 6, "md": 4}),
                            ]),

                            ft.Divider(),

                            ft.Text("Diámetros y Perímetros", size=18, weight="bold", color=PRIMARY_COLOR),
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
                            ft.Container(
                                content=details_table,
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
