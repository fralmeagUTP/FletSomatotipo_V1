import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import page_header, responsive_padding, set_busy
from src.frontend.longitudinal_analysis import build_longitudinal_panel
from src.frontend.navigation import show_dashboard


def AnalisisLongitudinalView(page: ft.Page):
    primary_color = theme.PRIMARY_COLOR
    text_color = theme.TEXT_COLOR
    api = ApiClient(page)

    current_rows = []
    current_athlete = None

    status_text = ft.Text(
        "Busca un deportista por nombre o ID para analizar su evolución corporal.",
        color=theme.SUBTITLE_COLOR,
        size=12,
    )
    content_area = ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)

    search_field = ft.TextField(
        label="Buscar deportista por nombre o ID",
        suffix_icon=ft.Icons.SEARCH,
        expand=True,
        text_size=14,
    )

    def period_label():
        if not current_rows:
            return "Sin periodo"
        dates = sorted(str(row.get("FECHA_MEDIDA", "")) for row in current_rows if row.get("FECHA_MEDIDA"))
        if not dates:
            return "Fechas no disponibles"
        if dates[0] == dates[-1]:
            return dates[0]
        return f"{dates[0]} → {dates[-1]}"

    def download_pdf(_=None):
        if hasattr(page, "run_thread"):
            page.run_thread(download_pdf_sync)
        else:
            download_pdf_sync()

    def download_pdf_sync():
        if not current_rows:
            show_snack(page, "No hay valoraciones para generar el PDF.")
            return
        identi = current_rows[0].get("IDENTI_DEPORTISTA")
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

    download_button = ft.Button(
        "Descargar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        disabled=True,
        on_click=download_pdf,
    )

    athlete_banner = ft.Container(visible=False)

    def render_athlete_banner():
        athlete_name = current_athlete.get("NOMBRE_DEPORTISTA", "Deportista") if current_athlete else "Deportista"
        athlete_id = current_athlete.get("IDENTI_DEPORTISTA", "") if current_athlete else ""
        athlete_banner.visible = True
        athlete_banner.content = ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Análisis longitudinal", size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                                ft.Text(athlete_name, size=16, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                                ft.Text(f"ID: {athlete_id}", size=12, color=theme.SUBTITLE_COLOR),
                            ],
                            spacing=3,
                        ),
                        col={"xs": 12, "md": 5},
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Valoraciones", size=12, color=theme.SUBTITLE_COLOR),
                                ft.Text(str(len(current_rows)), size=18, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                            ],
                            spacing=3,
                        ),
                        col={"xs": 6, "md": 2},
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Periodo", size=12, color=theme.SUBTITLE_COLOR),
                                ft.Text(period_label(), size=14, weight=ft.FontWeight.BOLD, color=theme.TEXT_COLOR),
                            ],
                            spacing=3,
                        ),
                        col={"xs": 6, "md": 3},
                    ),
                    ft.Container(
                        content=download_button,
                        col={"xs": 12, "md": 2},
                        alignment=ft.alignment.center_right,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                run_spacing=12,
            ),
            bgcolor=theme.CARD_BACKGROUND,
            border_radius=12,
            padding=16,
            shadow=theme.card_shadow(),
        )

    def render_empty(message):
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=primary_color, size=20),
                        ft.Text(message, color=theme.SUBTITLE_COLOR, expand=True),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                bgcolor=theme.INFO_BACKGROUND,
                border_radius=10,
                padding=14,
            )
        )
        athlete_banner.visible = False
        download_button.disabled = True

    def render_analysis():
        content_area.controls.clear()
        render_athlete_banner()
        content_area.controls.append(build_longitudinal_panel(current_rows))
        download_button.disabled = False

    def search_analysis(query):
        nonlocal current_rows, current_athlete
        query = (query or "").strip()
        if not query:
            current_rows = []
            current_athlete = None
            status_text.value = "Busca un deportista por nombre o ID para analizar su evolución corporal."
            render_empty("Sin búsqueda activa.")
            page.update()
            return

        controls = [search_button, download_button]
        set_busy(page, controls, True, status_text, "Buscando deportista...")
        try:
            athlete = api.find_deportista_for_historial(query)
            if not athlete:
                current_rows = []
                current_athlete = None
                status_text.value = "No se encontró deportista."
                render_empty("No se encontró un deportista con ese nombre o ID.")
                return

            current_athlete = athlete
            identi = athlete["IDENTI_DEPORTISTA"]
            current_rows = api.get_historial_vista_all(identi)
            status_text.value = f"Análisis de {athlete['NOMBRE_DEPORTISTA']} ({identi})"

            if len(current_rows) < 2:
                render_empty("Se requieren al menos dos valoraciones para generar un análisis longitudinal.")
                return

            render_analysis()
        except ApiError as error:
            current_rows = []
            current_athlete = None
            status_text.value = "No se pudo cargar el análisis."
            render_empty("No se pudo cargar el análisis longitudinal.")
            show_snack(page, str(error))
        except Exception as error:
            current_rows = []
            current_athlete = None
            status_text.value = "No se pudo cargar el análisis."
            render_empty("No se pudo cargar el análisis longitudinal.")
            show_snack(page, f"Error de conexión: {error}")
        finally:
            set_busy(page, controls, False)
            page.update()

    def run_search(_=None):
        query = search_field.value
        if hasattr(page, "run_thread"):
            page.run_thread(lambda: search_analysis(query))
        else:
            search_analysis(query)

    search_field.on_submit = lambda e: run_search()
    search_button = ft.IconButton(
        ft.Icons.SEARCH,
        icon_color=primary_color,
        tooltip="Buscar",
        on_click=run_search,
    )

    render_empty("Sin búsqueda activa.")

    search_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("Datos del deportista", size=16, weight=ft.FontWeight.BOLD, color=primary_color),
                ft.ResponsiveRow(
                    [
                        ft.Container(search_field, col={"xs": 10, "sm": 11}),
                        ft.Container(search_button, col={"xs": 2, "sm": 1}, alignment=ft.alignment.center),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                status_text,
            ],
            spacing=10,
        ),
        bgcolor=theme.CARD_BACKGROUND,
        border_radius=12,
        padding=16,
        shadow=theme.card_shadow(),
    )

    return ft.Container(
        content=ft.Column(
            [
                page_header("Análisis Longitudinal", on_back=lambda e: show_dashboard(page), color=text_color),
                ft.Container(height=10),
                search_card,
                ft.Container(height=12),
                athlete_banner,
                content_area,
            ],
            spacing=0,
            expand=True,
        ),
        padding=responsive_padding(page, desktop=20, tablet=16, mobile=10),
        bgcolor=theme.BACKGROUND_COLOR,
        expand=True,
    )
