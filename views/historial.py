import flet as ft
from app_config import show_snack
from src.frontend.composition_analysis import build_composition_panel
from src.frontend.components import page_header, page_width, responsive_padding, set_busy
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.assets import REFERENCE_IMAGES, asset_path
from src.frontend.interpretation import bmi_methodology_note
from src.frontend.longitudinal_analysis import build_longitudinal_panel
from src.frontend.navigation import show_dashboard
from src.frontend.somatocarta import build_somatocarta_card
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
    search_status = ft.Text("Busca por nombre o ID para ver el historial corporal.", color=theme.SUBTITLE_COLOR, size=12)
    current_page = 1
    page_size = 10
    total_count = 0
    current_historial_query = ""
    current_longitudinal_rows = []
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)
    # We need a reference to the layout containers to change visibility
    master_container = ft.Container(
        col={"xs": 12, "sm": 5, "md": 5, "lg": 4},
        bgcolor=theme.SURFACE_MUTED,
        padding=12,
        border_radius=10,
    )
    detail_container = ft.Container(
        col={"xs": 12, "sm": 7, "md": 7, "lg": 8},
        padding=12,
        bgcolor=CARD_BG,
        border_radius=10,
    )
    
    def update_layout():
        # Logic to toggle visibility based on screen width and selection
        page_width = page.width or 1024
        is_desktop = page_width >= 1024
        is_tablet = 768 <= page_width < 1024
        is_mobile = page_width < 768
        has_selection = bool(current_details_view.controls)
        
        if is_desktop:
            # Desktop: Both visible side by side
            master_container.visible = True
            detail_container.visible = True
            master_container.col = {"lg": 4, "md": 5}
            detail_container.col = {"lg": 8, "md": 7}
        elif is_tablet:
            # Tablet: Both visible but adjusted proportions
            master_container.visible = True
            detail_container.visible = True
            master_container.col = {"sm": 5, "md": 5}
            detail_container.col = {"sm": 7, "md": 7}
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

    def download_longitudinal_pdf(event):
        if not current_longitudinal_rows:
            show_snack(page, "No hay valoraciones para generar el PDF.")
            return
        identi = current_longitudinal_rows[0].get("IDENTI_DEPORTISTA")
        if not identi:
            show_snack(page, "No se encontró la identificación del deportista.")
            return
        try:
            path = api.download_longitudinal_pdf(identi)
            show_snack(page, f"PDF longitudinal guardado en: {path}")
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as error:
            show_snack(page, f"No se pudo generar el PDF: {error}")

    def show_longitudinal_analysis(_=None):
        if not current_longitudinal_rows:
            show_snack(page, "Busca un deportista con valoraciones para ver el análisis.")
            return
        current_details_view.controls.clear()
        current_details_view.controls.append(
            ft.ResponsiveRow(
                [
                    ft.Container(
                        ft.Text("Informe longitudinal", size=16, weight="bold", color=PRIMARY_COLOR),
                        col={"xs": 8, "sm": 9},
                    ),
                    ft.Container(
                        ft.Button(
                            "Descargar PDF",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=download_longitudinal_pdf,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            ),
                        ),
                        col={"xs": 4, "sm": 3},
                        alignment=ft.alignment.center_right,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        current_details_view.controls.append(build_longitudinal_panel(current_longitudinal_rows))
        update_layout()

    def load_details(somatotipo):
        """
        Muestra los detalles del somatotipo seleccionado en el panel derecho.
        """
        current_details_view.controls.clear()
        
        # Header Info - Responsive
        header_content = [
            ft.Text(f"Detalles - {somatotipo['FECHA_MEDIDA']}", size=18, weight="bold", color=PRIMARY_COLOR),
        ]
        if somatotipo.get("NOMBRE_DEPORTISTA"):
            header_content.append(ft.Text(f"Deportista: {somatotipo['NOMBRE_DEPORTISTA']}", weight="bold", size=14))
        
        # Add Demographics from View
        demog_text = []
        if somatotipo.get("EDAD"):
            demog_text.append(f"Edad: {somatotipo['EDAD']}")
        if somatotipo.get("SEXO_DEPORTISTA"):
            demog_text.append(f"Sexo: {somatotipo['SEXO_DEPORTISTA']}")
        
        if demog_text:
            header_content.append(ft.Text(" | ".join(demog_text), color="grey", size=12))

        current_details_view.controls.extend([
            ft.Column(header_content, spacing=4),
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
                    ft.Text(f"{label}: ", weight="bold", size=12),
                    ft.Text(str(value) if value is not None else "---", size=12)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

            def value_with_unit(value, unit):
                if value is None:
                    return "---"
                return f"{value} {unit}"

            def summary_box(label, value, subtitle=""):
                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(label, size=11, color=theme.SUBTITLE_COLOR, weight="w500"),
                            ft.Text(str(value) if value is not None else "---", size=20, weight="bold", color=TEXT_COLOR),
                            ft.Text(subtitle, size=10, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=2,
                    ),
                    bgcolor=theme.SURFACE_MUTED,
                    padding=10,
                    border_radius=8,
                    col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                )

            def interpretation_note(text):
                if not text:
                    return ft.Container(visible=False)
                return ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=theme.PRIMARY_COLOR, size=18),
                            ft.Text(text, size=12, color=theme.SUBTITLE_COLOR, expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    bgcolor=theme.INFO_BACKGROUND,
                    padding=10,
                    border_radius=8,
                )

            def reference_image_card(title, image_name, caption, aspect_ratio=1.35):
                available_width = min(max(page_width(page) - 96, 280), 920)
                image_width = available_width - 48
                image_height = round(image_width / aspect_ratio)
                image = ft.Image(
                    src=asset_path(image_name),
                    width=image_width,
                    height=image_height,
                    fit=ft.ImageFit.CONTAIN,
                )
                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(title, color=PRIMARY_COLOR, weight="bold", size=13),
                            ft.Container(
                                content=image,
                                alignment=ft.alignment.center,
                            ),
                            ft.Text(caption, size=11, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, "#e3e8f0"),
                    border_radius=10,
                    padding=12,
                    width=float("inf"),
                    col={"xs": 12},
                )

            somatotipo_id = det.get("id_Somatotipo")

            def download_pdf(_):
                pdf_button.disabled = True
                pdf_button.text = "Generando PDF..."
                page.update()
                try:
                    target_path = api.download_somatotipo_pdf(somatotipo_id)
                    show_snack(page, f"PDF descargado: {target_path}")
                    if hasattr(page, "launch_url"):
                        page.launch_url(target_path.as_uri())
                except ApiError as error:
                    show_snack(page, str(error))
                except Exception as error:
                    show_snack(page, f"No se pudo descargar el PDF: {error}")
                finally:
                    pdf_button.disabled = False
                    pdf_button.text = "Descargar PDF"
                    page.update()

            # --- Tabs for organized data ---
            tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Medidas",
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Antropometría básica", color=PRIMARY_COLOR, weight="bold", size=14),
                                ft.ResponsiveRow([
                                    ft.Container(info_row("Peso", value_with_unit(det.get('PESO_kg'), "kg")), col={"xs": 12, "sm": 6}),
                                    ft.Container(info_row("Estatura", value_with_unit(det.get('ESTA_USER_CM'), "cm")), col={"xs": 12, "sm": 6}),
                                ]),
                                ft.Divider(),
                                ft.Text("Pliegues (mm)", color=PRIMARY_COLOR, weight="bold", size=14),
                                ft.ResponsiveRow([
                                    ft.Container(info_row("Tricipital", value_with_unit(det.get('PLIEGUE_TRICIPITAL'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Subescapular", value_with_unit(det.get('PLIEGUE_SUBESCAPULAR'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Suprailiaco", value_with_unit(det.get('PLIEGUE_SUPRAILIACO'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Abdominal", value_with_unit(det.get('PLIEGUE_ABDOMINAL'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Muslo anterior", value_with_unit(det.get('PLIEGUE_MUSLO_ANT'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Pierna medial", value_with_unit(det.get('PLIEGUE_MEDIAL_PIERNA'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                ]),
                                ft.Divider(),
                                ft.Text("Diámetros y perímetros", color=PRIMARY_COLOR, weight="bold", size=14),
                                ft.ResponsiveRow([
                                    ft.Container(info_row("Diámetro muñeca", value_with_unit(det.get('DIAMETRO_BIEPI_MUNECA'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Diámetro fémur", value_with_unit(det.get('DIAMETRO_BIEPI_FEMUR'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Diámetro codo", value_with_unit(det.get('DIAMETRO_CODO'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Circunferencia carpo", value_with_unit(det.get('CIRCUNFERENCIA_CARPO'), "mm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Perímetro brazo", value_with_unit(det.get('PERIMETRO_BICED_CONTRAIDO'), "cm")), col={"xs": 12, "sm": 6, "md": 4}),
                                    ft.Container(info_row("Perímetro pierna", value_with_unit(det.get('PERIMETRO_PIERNA'), "cm")), col={"xs": 12, "sm": 6, "md": 4}),
                                ]),
                            ], spacing=10),
                            padding=10
                        ),
                    ),
                    ft.Tab(
                        text="Composición",
                        content=ft.Container(
                            content=build_composition_panel(det),
                            padding=10
                        ),
                    ),
                    ft.Tab(
                        text="Análisis",
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Análisis IMC", color=PRIMARY_COLOR, weight="bold", size=14),
                                    info_row("IMC", f"{value_with_unit(det.get('IMC'), 'kg/m²')} ({det.get('EstadoIMC') or '---'})"),
                                    interpretation_note(bmi_methodology_note(somatotipo.get("EDAD"), det.get("IMC"))),
                                    reference_image_card(
                                        "Referencia IMC",
                                        REFERENCE_IMAGES["imc"],
                                        "Apoyo visual para interpretar el índice de masa corporal y su clasificación.",
                                        aspect_ratio=0.79,
                                    ),
                                    ft.Divider(),
                                    ft.Text("Complexión física", color=PRIMARY_COLOR, weight="bold", size=14),
                                    info_row("Complexión", f"{det.get('Complexion') or '---'} ({det.get('TipoComplexion') or '---'})"),
                                    reference_image_card(
                                        "Referencia de contextura física",
                                        REFERENCE_IMAGES["contextura"],
                                        "Relaciona estatura, peso y complexión para contextualizar la valoración corporal.",
                                        aspect_ratio=1.45,
                                    ),
                                ],
                                spacing=10,
                            ),
                            padding=10
                        ),
                    ),
                    ft.Tab(
                        text="Somatotipo",
                        content=ft.Container(
                            content=ft.Column([
                                reference_image_card(
                                    "Referencia de somatotipos corporales",
                                    REFERENCE_IMAGES["somatotipos"],
                                    "Apoya la lectura de endomorfismo, mesomorfismo y ectomorfismo del deportista.",
                                    aspect_ratio=1.45,
                                ),
                                ft.Text("Componentes y Clasificación", color=PRIMARY_COLOR, weight="bold", size=14),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Endomorfismo:", weight="bold", size=13),
                                        ft.Text(f"{det.get('Endomorfismo')} - {det.get('EscalaEndomorfismo') or ''}", size=12),
                                        ft.Container(height=5),
                                        ft.Text("Mesomorfismo:", weight="bold", size=13),
                                        ft.Text(f"{det.get('Mesomorfismo')} - {det.get('EscalaMesomorfismo') or ''}", size=12),
                                        ft.Container(height=5),
                                        ft.Text("Ectomorfismo:", weight="bold", size=13),
                                        ft.Text(f"{det.get('Ectomorfismo')} - {det.get('EscalaEctomorfismo') or ''}", size=12),
                                    ]),
                                    padding=10,
                                    bgcolor=ft.Colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Text(f"Coordenadas: X={det.get('X')} , Y={det.get('Y')}", weight="bold", size=14, text_align="center"),
                                build_somatocarta_card(
                                    det.get("X"),
                                    det.get("Y"),
                                    somatotipo.get("NOMBRE_DEPORTISTA") or "",
                                ),
                            ], spacing=10),
                            padding=10
                        ),
                    ),
                ],
            )

            # Create a card for the detail containing the tabs
            current_details_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    ft.Text(f"Medición ID: {det.get('id_Somatotipo')}", size=12, color="grey"),
                                    col={"xs": 8, "sm": 9},
                                ),
                                ft.Container(
                                    (pdf_button := ft.Button(
                                        "Descargar PDF",
                                        icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=download_pdf,
                                        style=ft.ButtonStyle(
                                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                        ),
                                    )),
                                    col={"xs": 4, "sm": 3},
                                    alignment=ft.alignment.center_right,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.ResponsiveRow(
                            [
                                summary_box("IMC", det.get("IMC"), det.get("EstadoIMC") or ""),
                                summary_box("Endomorfismo", det.get("Endomorfismo"), det.get("EscalaEndomorfismo") or ""),
                                summary_box("Mesomorfismo", det.get("Mesomorfismo"), det.get("EscalaMesomorfismo") or ""),
                                summary_box("Ectomorfismo", det.get("Ectomorfismo"), det.get("EscalaEctomorfismo") or ""),
                            ],
                            spacing=10,
                            run_spacing=10,
                        ),
                        ft.Column(
                            [
                                ft.Text("Medidas", color=PRIMARY_COLOR, weight="bold", size=16),
                                tabs.tabs[0].content,
                                ft.Divider(),
                                ft.Text("Composición", color=PRIMARY_COLOR, weight="bold", size=16),
                                tabs.tabs[1].content,
                                ft.Divider(),
                                ft.Text("Análisis", color=PRIMARY_COLOR, weight="bold", size=16),
                                tabs.tabs[2].content,
                                ft.Divider(),
                                ft.Text("Somatotipo", color=PRIMARY_COLOR, weight="bold", size=16),
                                tabs.tabs[3].content,
                            ],
                            spacing=8,
                        )
                    ]),
                    padding=12,
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
    search_button = ft.IconButton(
        ft.Icons.SEARCH,
        icon_color=PRIMARY_COLOR,
        on_click=lambda e: search_historial(search_field.value, 1),
    )
    analysis_button = ft.Button(
        "Ver análisis",
        icon=ft.Icons.SHOW_CHART,
        disabled=True,
        on_click=show_longitudinal_analysis,
    )

    def search_historial(query, requested_page=1):
        nonlocal current_page, total_count, current_historial_query, current_longitudinal_rows
        current_page = max(1, requested_page)
        current_historial_query = query or ""
        if not query:
            search_status.value = "Busca por nombre o ID para ver el historial corporal."
            total_count = 0
            current_longitudinal_rows = []
            analysis_button.disabled = True
            update_pagination_controls()
            history_list.controls.clear()
            history_list.controls.append(ft.Text("Sin búsqueda activa."))
            history_list.update()
            page.update()
            return

        controls = [search_button, prev_button, next_button]
        set_busy(page, controls, True, search_status, "Buscando deportista...")
        try:
            athlete = api.find_deportista_for_historial(query)
            if not athlete:
                search_status.value = "No se encontró deportista."
                current_longitudinal_rows = []
                analysis_button.disabled = True
                render_history_list([])
                return

            identi = athlete["IDENTI_DEPORTISTA"]
            search_status.value = f"Historial de {athlete['NOMBRE_DEPORTISTA']} ({identi})"
            page_data = api.get_historial_vista_page(identi, current_page, page_size)
            analysis_data = api.get_historial_vista_page(identi, 1, 100)
            current_longitudinal_rows = analysis_data["items"]
            analysis_button.disabled = len(current_longitudinal_rows) < 2
            total_count = page_data["total"]
            update_pagination_controls()
            render_history_list(page_data["items"])
            if current_page == 1 and len(current_longitudinal_rows) >= 2:
                show_longitudinal_analysis()
        except ApiError as error:
            show_snack(page, str(error))
            search_status.value = "No se pudo cargar historial."
            total_count = 0
            current_longitudinal_rows = []
            analysis_button.disabled = True
            update_pagination_controls()
            history_list.controls.clear()
            history_list.controls.append(ft.Text("No se encontró historial."))
            history_list.update()
        except Exception as error:
            print(error)
            search_status.value = "No se pudo cargar historial."
            total_count = 0
            current_longitudinal_rows = []
            analysis_button.disabled = True
            update_pagination_controls()
            show_snack(page, f"Error de conexion: {error}")
        finally:
            for control in controls:
                control.disabled = False
            update_pagination_controls()
            page.update()
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
                    build_historial_item(sid, item, select_item, lambda _: None)
                )
        history_list.update()
        update_layout() # Ensure layout creates correctly based on empty data


    # Layout Components
    search_field = ft.TextField(
        label="Buscar deportista por nombre o ID",
        suffix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: search_historial(e.control.value, 1),
        expand=True,
        text_size=14,
    )

    def go_back(e):
        show_dashboard(page)

    # Responsive search row
    search_row = ft.ResponsiveRow(
        [
            ft.Container(search_field, col={"xs": 10, "sm": 11}),
            ft.Container(search_button, col={"xs": 2, "sm": 1}),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    main_container = ft.Container(
        content=ft.Column([
            # Top Bar
            page_header("Historial Corporal", on_back=go_back, color=TEXT_COLOR),
            ft.Container(height=10),
            
            # Search Area
            search_row,
            
            ft.Divider(),
            
            # Master-Detail Area
            ft.ResponsiveRow([
                    # Master (List)
                    master_container,
                    # Detail (View)
                    detail_container
                ], expand=True)
        ]),
        padding=responsive_padding(page, desktop=20, tablet=16, mobile=10),
        bgcolor=BG_COLOR,
        expand=True
    )

    # Initial Layout settings set content
    master_container.content = ft.Column([
        ft.Text("Registros", weight="bold", size=16),
        search_status,
        analysis_button,
        history_list,
        ft.Row(
            [
                prev_button,
                pagination_text,
                next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
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
