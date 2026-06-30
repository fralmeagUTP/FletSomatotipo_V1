import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.assets import REFERENCE_IMAGES
from src.frontend.components import mobile_search_field, page_header, page_width, pdf_action_button, responsive_padding, set_busy
from src.frontend.composition_analysis import build_composition_panel, mass_balance_message, mass_balance_summary
from src.frontend.interpretation import bmi_methodology_note, parse_float
from src.frontend.navigation import show_dashboard
from src.frontend.runtime import deliver_pdf, share_pdf
from src.frontend.somatocarta import build_somatocarta_card
from src.frontend.table_builders import build_historial_item, group_historial_rows


def HistorialView(page: ft.Page, initial_query=None):
    primary_color = theme.PRIMARY_COLOR
    background_color = theme.BACKGROUND_COLOR
    card_background = theme.CARD_BACKGROUND
    text_color = theme.TEXT_COLOR
    api = ApiClient(page)
    mobile_mode = page_width(page) < 700

    current_details_view = ft.ListView(spacing=14, expand=True)
    search_status = ft.Text("Busca por nombre o ID para ver el historial corporal.", color=theme.SUBTITLE_COLOR, size=12)
    current_page = 1
    page_size = 10
    total_count = 0
    current_historial_query = ""
    pagination_text = ft.Text("", color=theme.SUBTITLE_COLOR, size=13)

    master_container = ft.Container(
        col={"xs": 12, "sm": 5, "md": 5, "lg": 4},
        bgcolor=theme.SURFACE_MUTED,
        padding=12,
        border_radius=theme.RADIUS_MEDIUM,
    )
    detail_container = ft.Container(
        col={"xs": 12, "sm": 7, "md": 7, "lg": 8},
        padding=12,
        bgcolor=card_background,
        border_radius=theme.RADIUS_MEDIUM,
    )

    def update_layout():
        current_width = page.width or 1024
        is_desktop = current_width >= 1024
        is_tablet = 768 <= current_width < 1024
        has_selection = bool(current_details_view.controls)

        if is_desktop:
            master_container.visible = True
            detail_container.visible = True
            master_container.col = {"lg": 4, "md": 5}
            detail_container.col = {"lg": 8, "md": 7}
        elif is_tablet:
            master_container.visible = True
            detail_container.visible = True
            master_container.col = {"sm": 5, "md": 5}
            detail_container.col = {"sm": 7, "md": 7}
        else:
            master_container.visible = not has_selection
            detail_container.visible = has_selection
            master_container.col = {"xs": 12}
            detail_container.col = {"xs": 12}

        page.update()

    page.on_resized = lambda event: update_layout()

    def close_details(_=None):
        current_details_view.controls.clear()
        page._somatocarta_local_back_handler = None
        update_layout()

    def display(value, fallback="---"):
        if value in (None, ""):
            return fallback
        numeric_value = parse_float(value)
        if numeric_value is not None:
            return f"{numeric_value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def value_with_unit(value, unit):
        if value in (None, ""):
            return "---"
        return f"{display(value)} {unit}"

    def section_card(title, content, subtitle=None, icon=ft.Icons.INSIGHTS_OUTLINED):
        header_controls = [
            ft.Icon(icon, size=20, color=primary_color),
            ft.Column(
                [
                    ft.Text(title, color=primary_color, weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(subtitle, color=theme.SUBTITLE_COLOR, size=11, visible=bool(subtitle)),
                ],
                spacing=1,
                expand=True,
            ),
        ]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(header_controls, vertical_alignment=ft.CrossAxisAlignment.START, spacing=8),
                    content,
                ],
                spacing=12,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_LARGE,
            padding=14,
            width=float("inf"),
        )

    def metric_card(label, value, subtitle="", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, accent=None):
        accent = accent or primary_color
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=accent, size=18),
                            ft.Text(label, size=11, color=theme.SUBTITLE_COLOR, expand=True),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(display(value), size=20, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Text(display(subtitle, ""), size=10, color=theme.SUBTITLE_COLOR),
                ],
                spacing=4,
            ),
            bgcolor=theme.SURFACE_MUTED,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_MEDIUM,
            padding=12,
            col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
        )

    def data_chip(label, value, unit="", col=None):
        text_value = value_with_unit(value, unit) if unit else display(value)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=10, color=theme.SUBTITLE_COLOR),
                    ft.Text(text_value, size=12, color=text_color, weight=ft.FontWeight.BOLD),
                ],
                spacing=2,
            ),
            bgcolor="#ffffff",
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_SMALL,
            padding=10,
            col=col or {"xs": 12, "sm": 12, "md": 12, "lg": 12},
        )

    def insight_banner(text, icon=ft.Icons.INFO_OUTLINE, color=None, bgcolor=None):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color or primary_color, size=18),
                    ft.Text(text, size=12, color=theme.SUBTITLE_COLOR, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=8,
            ),
            bgcolor=bgcolor or theme.INFO_BACKGROUND,
            border_radius=theme.RADIUS_SMALL,
            padding=10,
        )

    def reference_image_card(title, image_name, caption, aspect_ratio=1.35, max_width=520):
        available_width = min(max(page_width(page) - 140, 220), max_width)
        image_height = round(available_width / aspect_ratio)
        image = ft.Image(
            src=image_name,
            width=available_width,
            height=image_height,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("No se pudo cargar la imagen de referencia.", color=theme.ERROR_COLOR),
        )
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, color=primary_color, weight=ft.FontWeight.BOLD, size=13),
                    ft.Container(content=image, alignment=ft.alignment.center),
                    ft.Text(caption, size=11, color=theme.SUBTITLE_COLOR),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_MEDIUM,
            padding=12,
            width=float("inf"),
            col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
        )

    def build_measurement_section(det):
        return section_card(
            "Medidas antropométricas",
            ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            data_chip("Peso", det.get("PESO_kg"), "kg"),
                            data_chip("Estatura", det.get("ESTA_USER_CM"), "cm"),
                            data_chip("IMC", det.get("IMC"), "kg/m²"),
                            data_chip("Complexión", f"{display(det.get('Complexion'))} ({display(det.get('TipoComplexion'))})"),
                        ],
                        spacing=8,
                        run_spacing=8,
                    ),
                    ft.Divider(height=8),
                    ft.Text("Pliegues cutáneos", color=primary_color, weight=ft.FontWeight.BOLD, size=13),
                    ft.ResponsiveRow(
                        [
                            data_chip("Tricipital", det.get("PLIEGUE_TRICIPITAL"), "mm"),
                            data_chip("Subescapular", det.get("PLIEGUE_SUBESCAPULAR"), "mm"),
                            data_chip("Suprailiaco", det.get("PLIEGUE_SUPRAILIACO"), "mm"),
                            data_chip("Abdominal", det.get("PLIEGUE_ABDOMINAL"), "mm"),
                            data_chip("Muslo anterior", det.get("PLIEGUE_MUSLO_ANT"), "mm"),
                            data_chip("Pierna medial", det.get("PLIEGUE_MEDIAL_PIERNA"), "mm"),
                        ],
                        spacing=8,
                        run_spacing=8,
                    ),
                    ft.Divider(height=8),
                    ft.Text("Diámetros y perímetros", color=primary_color, weight=ft.FontWeight.BOLD, size=13),
                    ft.ResponsiveRow(
                        [
                            data_chip("Muñeca", det.get("DIAMETRO_BIEPI_MUNECA"), "mm"),
                            data_chip("Fémur", det.get("DIAMETRO_BIEPI_FEMUR"), "mm"),
                            data_chip("Codo", det.get("DIAMETRO_CODO"), "mm"),
                            data_chip("Carpo", det.get("CIRCUNFERENCIA_CARPO"), "cm"),
                            data_chip("Brazo", det.get("PERIMETRO_BICED_CONTRAIDO"), "cm"),
                            data_chip("Pierna", det.get("PERIMETRO_PIERNA"), "cm"),
                        ],
                        spacing=8,
                        run_spacing=8,
                    ),
                ],
                spacing=10,
            ),
            "Datos base usados por las ecuaciones y la somatocarta.",
            ft.Icons.STRAIGHTEN,
        )

    def build_reading_section(somatotipo, det):
        balance = mass_balance_summary(det)
        balance_text = mass_balance_message(balance)
        bmi_note = bmi_methodology_note(somatotipo.get("EDAD"), det.get("IMC"))
        insights = [
            insight_banner("Método principal de composición: Yuhasz para población deportiva. Faulkner se conserva como referencia comparativa."),
            insight_banner(bmi_note) if bmi_note else ft.Container(visible=False),
        ]
        if balance_text:
            insights.append(
                insight_banner(
                    balance_text,
                    icon=ft.Icons.WARNING_AMBER_ROUNDED if balance and balance["is_warning"] else ft.Icons.CHECK_CIRCLE_OUTLINE,
                    color=theme.WARNING_COLOR if balance and balance["is_warning"] else theme.SUCCESS_COLOR,
                    bgcolor="#fff7ed" if balance and balance["is_warning"] else "#ecfdf3",
                )
            )
        return section_card(
            "Lectura rápida",
            ft.Column(insights, spacing=8),
            "Resumen interpretativo para orientar la decisión del evaluador.",
            ft.Icons.PSYCHOLOGY_ALT_OUTLINED,
        )

    def build_reference_section(somatotipo, det):
        return section_card(
            "Análisis y referencias",
            ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Análisis IMC", color=primary_color, weight=ft.FontWeight.BOLD, size=14),
                                        data_chip("IMC", f"{value_with_unit(det.get('IMC'), 'kg/m²')} ({display(det.get('EstadoIMC'))})", "", {"xs": 12}),
                                        insight_banner(bmi_methodology_note(somatotipo.get("EDAD"), det.get("IMC")) or "Sin nota metodológica disponible."),
                                    ],
                                    spacing=8,
                                ),
                                col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
                            ),
                            reference_image_card(
                                "Referencia IMC",
                                REFERENCE_IMAGES["imc"],
                                "Apoyo visual para interpretar el índice de masa corporal y su clasificación.",
                                aspect_ratio=0.79,
                                max_width=520,
                            ),
                        ],
                        spacing=12,
                        run_spacing=12,
                    ),
                    ft.Divider(height=8),
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Complexión física", color=primary_color, weight=ft.FontWeight.BOLD, size=14),
                                        data_chip("Complexión", f"{display(det.get('Complexion'))} ({display(det.get('TipoComplexion'))})", "", {"xs": 12}),
                                        insight_banner("Relaciona estatura, peso y complexión para contextualizar la valoración corporal."),
                                    ],
                                    spacing=8,
                                ),
                                col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
                            ),
                            reference_image_card(
                                "Referencia de contextura física",
                                REFERENCE_IMAGES["contextura"],
                                "Tabla de apoyo para contrastar la complexión calculada.",
                                aspect_ratio=1.45,
                                max_width=560,
                            ),
                        ],
                        spacing=12,
                        run_spacing=12,
                    ),
                ],
                spacing=12,
            ),
            "IMC y complexión se muestran como apoyos, no como diagnóstico aislado.",
            ft.Icons.QUERY_STATS,
        )

    def build_somatotype_section(somatotipo, det):
        component_cards = ft.ResponsiveRow(
            [
                metric_card("Endomorfismo", det.get("Endomorfismo"), det.get("EscalaEndomorfismo") or "", ft.Icons.ACCESSIBILITY_NEW, theme.WARNING_COLOR),
                metric_card("Mesomorfismo", det.get("Mesomorfismo"), det.get("EscalaMesomorfismo") or "", ft.Icons.FITNESS_CENTER, primary_color),
                metric_card("Ectomorfismo", det.get("Ectomorfismo"), det.get("EscalaEctomorfismo") or "", ft.Icons.DIRECTIONS_RUN, theme.SUCCESS_COLOR),
                metric_card("Coordenada X", det.get("X"), "Somatocarta", ft.Icons.TRIP_ORIGIN, primary_color),
                metric_card("Coordenada Y", det.get("Y"), "Somatocarta", ft.Icons.TRIP_ORIGIN, primary_color),
            ],
            spacing=8,
            run_spacing=8,
        )
        return section_card(
            "Somatotipo y somatocarta",
            ft.Column(
                [
                    component_cards,
                    reference_image_card(
                        "Referencia de somatotipos corporales",
                        REFERENCE_IMAGES["somatotipos"],
                        "Apoya la lectura de endomorfismo, mesomorfismo y ectomorfismo.",
                        aspect_ratio=1.45,
                        max_width=640,
                    ),
                    ft.Container(
                        content=build_somatocarta_card(
                            det.get("X"),
                            det.get("Y"),
                            somatotipo.get("NOMBRE_DEPORTISTA") or "",
                        ),
                        width=float("inf"),
                    ),
                ],
                spacing=12,
            ),
            "Clasificación somática y ubicación gráfica de la valoración.",
            ft.Icons.GRID_ON,
        )

    def build_detail_card(somatotipo, det):
        somatotipo_id = det.get("id_Somatotipo")

        def download_pdf(_):
            if hasattr(page, "run_thread"):
                page.run_thread(download_pdf_sync)
            else:
                download_pdf_sync()

        def download_pdf_sync():
            pdf_button.disabled = True
            pdf_button.text = "Generando PDF..."
            page.update()
            try:
                delivery = share_pdf if mobile_mode else deliver_pdf
                target = delivery(
                    page,
                    api.get_somatotipo_pdf_bytes(somatotipo_id),
                    f"valoracion_{somatotipo_id}.pdf",
                )
                show_snack(page, f"PDF generado: {target}")
            except ApiError as error:
                show_snack(page, str(error))
            except Exception as error:
                show_snack(page, f"No se pudo descargar el PDF: {error}")
            finally:
                pdf_button.disabled = False
                pdf_button.text = "Compartir PDF" if mobile_mode else "Descargar PDF"
                page.update()

        pdf_button = pdf_action_button(download_pdf, mobile=mobile_mode)
        close_button = ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver al listado", on_click=close_details, icon_color=primary_color)

        header = ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                close_button,
                                ft.Column(
                                    [
                                        ft.Text("Análisis de valoración corporal", size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                                        ft.Text(display(somatotipo.get("NOMBRE_DEPORTISTA"), "Deportista"), size=14, weight=ft.FontWeight.BOLD, color=text_color),
                                        ft.Text(f"Fecha: {display(somatotipo.get('FECHA_MEDIDA'))} · Medición ID: {display(somatotipo_id)}", size=12, color=theme.SUBTITLE_COLOR),
                                    ],
                                    spacing=3,
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
                    ),
                    ft.Container(
                        content=pdf_button,
                        alignment=ft.alignment.center_right,
                        col={"xs": 12, "sm": 12, "md": 12, "lg": 12},
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                run_spacing=12,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_LARGE,
            padding=14,
        )

        kpis = ft.ResponsiveRow(
            [
                metric_card("IMC", value_with_unit(det.get("IMC"), "kg/m²"), det.get("EstadoIMC") or "", ft.Icons.MONITOR_WEIGHT_OUTLINED),
                metric_card("Grasa Yuhasz", value_with_unit(det.get("PorcRasoYuasz"), "%"), "Método principal", ft.Icons.PIE_CHART_OUTLINE, theme.WARNING_COLOR),
                metric_card("Masa muscular", value_with_unit(det.get("Mma"), "kg"), "Composición", ft.Icons.FITNESS_CENTER, primary_color),
                metric_card(
                    "Somatotipo",
                    f"{display(det.get('Endomorfismo'))} - {display(det.get('Mesomorfismo'))} - {display(det.get('Ectomorfismo'))}",
                    "Endo · Meso · Ecto",
                    ft.Icons.ACCESSIBILITY_NEW,
                    primary_color,
                ),
            ],
            spacing=8,
            run_spacing=8,
        )

        return ft.Container(
            content=ft.Column(
                [
                    header,
                    kpis,
                    build_reading_section(somatotipo, det),
                    build_measurement_section(det),
                    section_card(
                        "Composición corporal",
                        build_composition_panel(det),
                        "Comparación de métodos de grasa, balance de masas y distribución corporal.",
                        ft.Icons.DONUT_LARGE,
                    ),
                    build_reference_section(somatotipo, det),
                    build_somatotype_section(somatotipo, det),
                ],
                spacing=12,
            ),
            padding=0,
            width=float("inf"),
        )

    def load_details(somatotipo):
        current_details_view.controls.clear()
        if mobile_mode:
            page._somatocarta_local_back_handler = lambda: (close_details(), True)[1]
        detalles = somatotipo.get("detalles", [])
        if not detalles:
            current_details_view.controls.append(ft.Text("No hay detalles registrados."))
            current_details_view.update()
            return

        for det in detalles:
            current_details_view.controls.append(build_detail_card(somatotipo, det))
        current_details_view.update()

    def update_pagination_controls():
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        pagination_text.value = f"Página {current_page} de {total_pages}"
        prev_button.disabled = current_page <= 1
        next_button.disabled = current_page >= total_pages

    def change_history_page(delta):
        run_search_historial(current_historial_query or search_field.value, current_page + delta)

    prev_button = ft.IconButton(
        ft.Icons.CHEVRON_LEFT,
        icon_color=primary_color,
        tooltip="Página anterior",
        on_click=lambda event: change_history_page(-1),
    )
    next_button = ft.IconButton(
        ft.Icons.CHEVRON_RIGHT,
        icon_color=primary_color,
        tooltip="Página siguiente",
        on_click=lambda event: change_history_page(1),
    )
    search_button = ft.IconButton(
        ft.Icons.SEARCH,
        icon_color=primary_color,
        on_click=lambda event: run_search_historial(search_field.value, 1),
    )

    def render_history_list(data):
        history_list.controls.clear()
        if not data:
            history_list.controls.append(ft.Text("Sin registros."))
            current_details_view.controls.clear()
        else:
            grouped = group_historial_rows(data)

            def select_item(item):
                load_details(item)
                update_layout()

            for sid, item in grouped.items():
                history_list.controls.append(build_historial_item(sid, item, select_item, lambda _: None))
        history_list.update()
        update_layout()

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

        controls = [search_button, prev_button, next_button]
        set_busy(page, controls, True, search_status, "Buscando deportista...")
        try:
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
            search_status.value = "No se pudo cargar historial."
            total_count = 0
            update_pagination_controls()
            show_snack(page, f"Error de conexión: {error}")
        finally:
            for control in controls:
                control.disabled = False
            update_pagination_controls()
            page.update()

    def run_search_historial(query, requested_page=1):
        if hasattr(page, "run_thread"):
            page.run_thread(lambda: search_historial(query, requested_page))
        else:
            search_historial(query, requested_page)

    history_list = ft.ListView(
        expand=True,
        spacing=10,
        controls=[ft.Text("Sin búsqueda activa.")],
    )

    if mobile_mode:
        search_field = mobile_search_field(
            "Buscar deportista por nombre o ID",
            value=initial_query or "",
            on_search=lambda query: run_search_historial(query, 1),
        )
        search_row = ft.Container(search_field)
    else:
        search_field = ft.TextField(
            label="Buscar deportista por nombre o ID",
            value=initial_query or "",
            suffix_icon=ft.Icons.SEARCH,
            on_submit=lambda event: run_search_historial(event.control.value, 1),
            expand=True,
            text_size=14,
        )
        search_row = ft.ResponsiveRow(
            [
                ft.Container(search_field, col={"xs": 10, "sm": 11}),
                ft.Container(search_button, col={"xs": 2, "sm": 1}),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    master_container.content = ft.Column(
        [
            ft.Text("Registros", weight=ft.FontWeight.BOLD, size=16),
            search_status,
            history_list,
            ft.Row(
                [prev_button, pagination_text, next_button],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=10,
    )
    detail_container.content = current_details_view
    master_container.visible = True
    detail_container.visible = False

    view = ft.Container(
        content=ft.Column(
            [
                page_header("Historial Corporal", on_back=lambda event: show_dashboard(page), color=text_color),
                ft.Container(height=10),
                search_row,
                ft.Divider(),
                ft.ResponsiveRow([master_container, detail_container], expand=True),
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        padding=responsive_padding(page, desktop=20, tablet=16, mobile=10),
        bgcolor=background_color,
        expand=True,
    )
    if initial_query:
        return view, lambda: search_historial(initial_query, 1)
    return view
