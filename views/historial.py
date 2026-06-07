import flet as ft
from app_config import show_snack
from src.frontend.components import page_header
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.navigation import show_dashboard
from src.frontend.table_builders import build_historial_item, group_historial_rows
from src.frontend import theme

def HistorialView(page: ft.Page):
    """
    Vista de Historial de Somatotipos.
    Muestra una lista de valoraciones (Encabezados) y permite ver el detalle de cada una.
    """
    # Colors
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    BG_COLOR = theme.BACKGROUND_COLOR
    CARD_BG = theme.CARD_BACKGROUND
    TEXT_COLOR = theme.TEXT_COLOR

    # State
    api = ApiClient(page)
    current_details_view = ft.Column(scroll=ft.ScrollMode.AUTO)
    search_status = ft.Text("Busca por nombre o ID para ver el historial corporal.", color=theme.SUBTITLE_COLOR, size=13)
    current_page = 1
    page_size = 10
    total_count = 0
    current_historial_query = ""
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    # We need a reference to the layout containers to change visibility
    master_container = ft.Container(col={"xs": 12, "md": 4}, bgcolor=theme.SURFACE_MUTED, padding=10, border_radius=10)
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
                                ft.ResponsiveRow([
                                    ft.Container(info_row("Peso (kg)", det.get('PESO_kg')), col=6),
                                    ft.Container(info_row("Estatura (cm)", det.get('ESTA_USER_CM')), col=6),
                                ]),
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


    def update_pagination_controls():
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        pagination_text.value = f"Página {current_page} de {total_pages}"
        prev_button.disabled = current_page <= 1
        next_button.disabled = current_page >= total_pages

    def change_history_page(delta):
        search_historial(current_historial_query or search_field.value, current_page + delta)

    prev_button = ft.IconButton(
        ft.Icons.CHEVRON_LEFT,
        icon_color=PRIMARY_COLOR,
        tooltip="Página anterior",
        on_click=lambda e: change_history_page(-1),
    )
    next_button = ft.IconButton(
        ft.Icons.CHEVRON_RIGHT,
        icon_color=PRIMARY_COLOR,
        tooltip="Página siguiente",
        on_click=lambda e: change_history_page(1),
    )

    def search_historial(query, requested_page=1):
        nonlocal current_page, total_count, current_historial_query
        current_page = max(1, requested_page)
        current_historial_query = query or ""
        if not query:
            search_status.value = "Busca por nombre o ID para ver el historial corporal."
            total_count = 0
            update_pagination_controls()
            history_list.controls.clear()
            history_list.controls.append(ft.Text("Sin búsqueda activa."))
            history_list.update()
            page.update()
            return

        try:
            search_status.value = "Buscando deportista..."
            page.update()
            athlete = api.find_deportista_for_historial(query)
            if not athlete:
                search_status.value = "No se encontró deportista."
                render_history_list([])
                return

            identi = athlete["IDENTI_DEPORTISTA"]
            search_status.value = f"Historial de {athlete['NOMBRE_DEPORTISTA']} ({identi})"
            page_data = api.get_historial_vista_page(identi, current_page, page_size)
            total_count = page_data["total"]
            update_pagination_controls()
            render_history_list(page_data["items"])
        except ApiError as error:
            show_snack(page, str(error))
            search_status.value = "No se pudo cargar historial."
            total_count = 0
            update_pagination_controls()
            history_list.controls.clear()
            history_list.controls.append(ft.Text("No se encontró historial."))
            history_list.update()
        except Exception as error:
            print(error)
            search_status.value = "No se pudo cargar historial."
            total_count = 0
            update_pagination_controls()
            show_snack(page, f"Error de conexion: {error}")
    history_list = ft.ListView(
        expand=True,
        spacing=10,
        controls=[ft.Text("Sin búsqueda activa.")],
    )

    
    def delete_somatotipo(sid):
        def close_dlg(e):
            page.dialog.open = False
            page.update()

        def confirm_delete(e):
            try:
                api.delete_somatotipo(sid)
                show_snack(page, "Registro eliminado correctamente")
                search_historial(search_field.value, current_page)
                current_details_view.controls.clear()
                update_layout()
            except ApiError as error:
                show_snack(page, str(error))
            except Exception as error:
                print(error)
                show_snack(page, f"Error de conexion: {error}")
            finally:
                page.dialog.open = False
                page.update()
    def render_history_list(data):
        history_list.controls.clear()
        if not data:
            history_list.controls.clear()
            history_list.controls.append(ft.Text("Sin registros."))
            current_details_view.controls.clear()
        else:
            grouped = group_historial_rows(data)

            def select_item(item):
                load_details(item)
                update_layout()

            history_list.controls.clear()
            for sid, item in grouped.items():
                history_list.controls.append(
                    build_historial_item(sid, item, select_item, delete_somatotipo)
                )
        history_list.update()
        update_layout() # Ensure layout creates correctly based on empty data


    # Layout Components
    search_field = ft.TextField(
        label="Buscar deportista por nombre o ID",
        suffix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: search_historial(e.control.value, 1),
        expand=True
    )

    def go_back(e):
        show_dashboard(page)

    main_container = ft.Container(
        content=ft.Column([
            # Top Bar
            page_header("Historial Corporal", on_back=go_back, color=TEXT_COLOR),
            ft.Container(height=10),
            
            # Search Area
            ft.Row([search_field, ft.IconButton(ft.Icons.SEARCH, icon_color=PRIMARY_COLOR, on_click=lambda e: search_historial(search_field.value, 1))]),
            
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
        search_status,
        history_list,
        ft.Row(
            [
                prev_button,
                pagination_text,
                next_button,
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
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
