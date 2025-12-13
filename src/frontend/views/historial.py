import flet as ft
import requests

API_URL = "http://127.0.0.1:8085"

def HistorialView(page: ft.Page):
    """
    Vista de Historial de Somatotipos.
    Muestra una lista de valoraciones (Encabezados) y permite ver el detalle de cada una.
    """
    # Colors
    PRIMARY_COLOR = "#2e5cb8"
    BG_COLOR = "#f5f7fb"
    CARD_BG = ft.Colors.WHITE
    TEXT_COLOR = "#333333"

    # State
    current_details_view = ft.Column(scroll=ft.ScrollMode.AUTO)
    # We need a reference to the layout containers to change visibility
    master_container = ft.Container(col={"xs": 12, "md": 4}, bgcolor="#f0f2f5", padding=10, border_radius=10)
    detail_container = ft.Container(col={"xs": 12, "md": 8}, padding=10, bgcolor=CARD_BG, border_radius=10)
    
    def update_layout():
        # Logic to toggle visibility based on screen width and selection
        is_large_screen = page.width >= 768
        has_selection = bool(current_details_view.controls)
        
        if is_large_screen:
            # Desktop: Both visible
            master_container.visible = True
            detail_container.visible = True
            master_container.col = {"md": 4}
            detail_container.col = {"md": 8}
        else:
            # Mobile: One or the other
            if has_selection:
                master_container.visible = False
                detail_container.visible = True
                detail_container.col = {"xs": 12}
            else:
                master_container.visible = True
                detail_container.visible = False
                master_container.col = {"xs": 12}
        
        page.update()

    # Hook resize
    def on_resize(e):
        update_layout()
        
    page.on_resized = on_resize

    def close_details(e):
        current_details_view.controls.clear()
        update_layout()

    def load_details(somatotipo):
        """
        Muestra los detalles del somatotipo seleccionado en el panel derecho.
        """
        current_details_view.controls.clear()
        
        # Header Info with Close Button for Mobile
        header_content = [
            ft.Row([
                ft.Text(f"Detalles - {somatotipo['FECHA_MEDIDA']}", size=20, weight="bold", color=PRIMARY_COLOR, expand=True),
                ft.IconButton(ft.Icons.CLOSE, icon_color="red", on_click=close_details)
            ]),
        ]
        if somatotipo.get("NOMBRE_DEPORTISTA"):
            header_content.append(ft.Text(f"Deportista: {somatotipo['NOMBRE_DEPORTISTA']}", weight="bold"))
        
        # Add Demographics from View
        demog_text = []
        if somatotipo.get("EDAD"):
            demog_text.append(f"Edad: {somatotipo['EDAD']}")
        if somatotipo.get("SEXO_DEPORTISTA"):
            demog_text.append(f"Sexo: {somatotipo['SEXO_DEPORTISTA']}")
        
        if demog_text:
            header_content.append(ft.Text(" | ".join(demog_text), color="grey"))

        current_details_view.controls.extend([
            ft.Column(header_content),
            ft.Divider()
        ])

        # Details List (Should usually be just one per header based on current logic, but 1-to-N supported)
        detalles = somatotipo.get("detalles", [])
        
        if not detalles:
            current_details_view.controls.append(ft.Text("No hay detalles registrados."))
        
        for det in detalles:
            # Helper for rows
            def info_row(label, value):
                return ft.Row([
                    ft.Text(f"{label}: ", weight="bold", size=13),
                    ft.Text(str(value) if value is not None else "---", size=13)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

            # --- Tabs for organized data ---
            tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Medidas",
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Antropometría Básica", color=PRIMARY_COLOR, weight="bold"),
                                ft.Row([
                                    info_row("Peso (kg)", det.get('PESO_kg')),
                                    info_row("Estatura (cm)", det.get('ESTA_USER_CM')),
                                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                ft.Divider(),
                                ft.Text("Pliegues (mm)", color=PRIMARY_COLOR, weight="bold"),
                                ft.ResponsiveRow([
                                    ft.Container(info_row("Tricipital", det.get('PLIEGUE_TRICIPITAL')), col=6),
                                    ft.Container(info_row("Subesc.", det.get('PLIEGUE_SUBESCAPULAR')), col=6),
                                    ft.Container(info_row("Supraili.", det.get('PLIEGUE_SUPRAILIACO')), col=6),
                                    ft.Container(info_row("Abdom.", det.get('PLIEGUE_ABDOMINAL')), col=6),
                                    ft.Container(info_row("Muslo", det.get('PLIEGUE_MUSLO_ANT')), col=6),
                                    ft.Container(info_row("Pierna", det.get('PLIEGUE_MEDIAL_PIERNA')), col=6),
                                ]),
                                ft.Divider(),
                                ft.Text("Diámetros y Perímetros", color=PRIMARY_COLOR, weight="bold"),
                                ft.ResponsiveRow([
                                    ft.Container(info_row("D. Muñeca", det.get('DIAMETRO_BIEPI_MUNECA')), col=6),
                                    ft.Container(info_row("D. Fémur", det.get('DIAMETRO_BIEPI_FEMUR')), col=6),
                                    ft.Container(info_row("D. Codo", det.get('DIAMETRO_CODO')), col=6),
                                    ft.Container(info_row("C. Carpo", det.get('CIRCUNFERENCIA_CARPO')), col=6),
                                    ft.Container(info_row("P. Brazo", det.get('PERIMETRO_BICED_CONTRAIDO')), col=6),
                                    ft.Container(info_row("P. Pierna", det.get('PERIMETRO_PIERNA')), col=6),
                                ]),
                            ], scroll=ft.ScrollMode.AUTO),
                            padding=10
                        ),
                    ),
                    ft.Tab(
                        text="Composición",
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Porcentajes Grasos (%)", color=PRIMARY_COLOR, weight="bold"),
                                info_row("Yuhasz", det.get('PorcRasoYuasz')),
                                info_row("Faulkner", det.get('PorcGrasoFaulker')),
                                info_row("Jackson/Pollock", det.get('PorcGrasoJonson')),
                                ft.Divider(),
                                ft.Text("Masas (kg)", color=PRIMARY_COLOR, weight="bold"),
                                info_row("Masa Grasa (Yuhasz)", det.get('PesoRasoYuazs')),
                                info_row("Masa Grasa (Faulkner)", det.get('PesoRasoFaulker')),
                                info_row("Masa Grasa (Jackson)", det.get('PesoGrasoJhonston')),
                                info_row("Masa Osea", det.get('PesoOseo')),
                                info_row("Masa Residual", det.get('PesoResidual')),
                                info_row("Masa Muscular", det.get('Mma')),
                            ], scroll=ft.ScrollMode.AUTO),
                            padding=10
                        ),
                    ),
                    ft.Tab(
                        text="Somatotipo",
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Componentes y Clasificación", color=PRIMARY_COLOR, weight="bold"),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Endomorfismo:", weight="bold"),
                                        ft.Text(f"{det.get('Endomorfismo')} - {det.get('EscalaEndomorfismo') or ''}"),
                                        ft.Container(height=5),
                                        ft.Text("Mesomorfismo:", weight="bold"),
                                        ft.Text(f"{det.get('Mesomorfismo')} - {det.get('EscalaMesomorfismo') or ''}"),
                                        ft.Container(height=5),
                                        ft.Text("Ectomorfismo:", weight="bold"),
                                        ft.Text(f"{det.get('Ectomorfismo')} - {det.get('EscalaEctomorfismo') or ''}"),
                                    ]),
                                    padding=10,
                                    bgcolor=ft.Colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Container(height=10),
                                ft.Text(f"Coordenadas: X={det.get('X')} , Y={det.get('Y')}", weight="bold", size=16, text_align="center"),
                                ft.Divider(),
                                ft.Text("Análisis", color=PRIMARY_COLOR, weight="bold"),
                                info_row("IMC", f"{det.get('IMC')} ({det.get('EstadoIMC')})"),
                                info_row("Complexión", f"{det.get('Complexion')} ({det.get('TipoComplexion')})"),
                            ], scroll=ft.ScrollMode.AUTO),
                            padding=10
                        ),
                    ),
                ],
                expand=True,
            )

            # Create a card for the detail containing the tabs
            current_details_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Medición ID: {det.get('id_Somatotipo')}", size=12, color="grey"), # Using Somatotipo ID or Index
                        ft.Container(content=tabs, height=400) # Fixed height for tabs area
                    ]),
                    padding=10,
                    border=ft.border.all(1, "#eeeeee"),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE
                )
            )
            
        current_details_view.update()


    def search_historial(query):
        if not query:
            return
            
        # 1. Search athletes first to get ID (or assuming query is ID)
        # Ideally we'd search athlete name, get ID, then fetch history. 
        # For now let's assume query is ID for simplicity, or we reuse the athlete search logic.
        
        # Let's try to fetch by ID directly
        try:
             resp = requests.get(f"{API_URL}/somatotipo/vista/deportista/{query}")
             if resp.status_code == 200:
                 data = resp.json()
                 render_history_list(data)
             else:
                 # If empty check if it was a name search... (omitted for brevity, assuming ID)
                 history_list.controls.clear()
                 history_list.controls.append(ft.Text("No se encontró historial."))
                 history_list.update()
        except Exception as e:
            print(e)

    history_list = ft.ListView(expand=True, spacing=10)

    
    def delete_somatotipo(sid):
        def close_dlg(e):
            page.dialog.open = False
            page.update()

        def confirm_delete(e):
            try:
                resp = requests.delete(f"{API_URL}/somatotipo/{sid}")
                if resp.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Registro eliminado correctamente"))
                    page.snack_bar.open = True
                    # Refresh list
                    search_historial(search_field.value)
                    # Clear details if deleted one was showing
                    current_details_view.controls.clear()
                    update_layout()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Error al eliminar"))
                    page.snack_bar.open = True
            except Exception as ex:
                print(ex)
            finally:
                page.dialog.open = False
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Estás seguro de que deseas eliminar este registro y todos sus detalles?"),
            actions=[
                ft.TextButton("Sí, eliminar", on_click=confirm_delete),
                ft.TextButton("Cancelar", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def render_history_list(data):
        history_list.controls.clear()
        if not data:
            history_list.controls.clear()
            history_list.controls.append(ft.Text("Sin registros."))
            current_details_view.controls.clear()
        else:
            # Group flat view data by Somatotype ID
            grouped = {}
            for row in data:
                sid = row['id_Somatotipo']
                if sid not in grouped:
                    grouped[sid] = {
                        'FECHA_MEDIDA': row['FECHA_MEDIDA'],
                        'NOMBRE_DEPORTISTA': row.get('NOMBRE_DEPORTISTA', ''), # Add Name
                        'EDAD': row.get('EDAD'),
                        'SEXO_DEPORTISTA': row.get('SEXO_DEPORTISTA'),
                        'detalles': []
                    }
                # Add Detail
                grouped[sid]['detalles'].append(row)

            history_list.controls.clear()
            for sid, item in grouped.items():
                history_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"Fecha: {item['FECHA_MEDIDA']}", weight="bold"),
                                ft.Text(f"{item['NOMBRE_DEPORTISTA']}", size=12, no_wrap=True, color="#666666"),
                            ], expand=True),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE, 
                                icon_color="red", 
                                tooltip="Eliminar Evaluación",
                                on_click=lambda e, s_id=sid: delete_somatotipo(s_id)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8,
                        on_click=lambda e, s=item: [load_details(s), update_layout()], # Update layout on click
                        ink=True,
                        border=ft.border.all(1, "#dddddd")
                    )
                )
        history_list.update()
        update_layout() # Ensure layout creates correctly based on empty data


    # Layout Components
    search_field = ft.TextField(
        label="ID Deportista", 
        suffix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: search_historial(e.control.value),
        expand=True
    )

    def go_back(e):
        from .dashboard import DashboardView
        page.clean()
        page.add(DashboardView(page))

    main_container = ft.Container(
        content=ft.Column([
            # Top Bar
             ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back, icon_color=TEXT_COLOR),
                    ft.Text("Historial Corporal", size=32, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Container(height=10),
            
            # Search Area
            ft.Row([search_field, ft.IconButton(ft.Icons.SEARCH, icon_color=PRIMARY_COLOR, on_click=lambda e: search_historial(search_field.value))]),
            
            ft.Divider(),
            
            # Master-Detail Area
            ft.ResponsiveRow([
                    # Master (List)
                    master_container,
                    # Detail (View)
                    detail_container
                ], expand=True)
        ]),
        padding=20,
        bgcolor=BG_COLOR,
        expand=True
    )

    # Initial Layout settings set content
    master_container.content = ft.Column([
        ft.Text("Registros", weight="bold"),
        history_list
    ])
    detail_container.content = current_details_view
    
    # Run initial layout check specifically after adding to page usually, but here we return container.
    # We can't guarantee page.width is ready until view is mounted.
    # But we can try default state (Master visible, Detail hidden if empty)
    master_container.visible = True
    detail_container.visible = False # Hidden by default until selection

    return main_container

    # NOTE: The return structure changed to 'main_container' which we need to define at top of layout block
    pass
