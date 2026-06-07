import flet as ft
from src.frontend.components import info_banner, page_header
from src.frontend.navigation import show_deportistas, show_historial, show_valoracion
from src.frontend import theme

def DashboardView(page: ft.Page):
    """
    Vista del Dashboard principal.

    Muestra el menú de opciones principales: Deportistas, Valoración, Historial, etc.

    Args:
        page (ft.Page): La referencia a la página principal de Flet.

    Returns:
        ft.Container: El contenedor principal con el diseño del dashboard.
    """
    # Colors
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    BG_COLOR = theme.BACKGROUND_COLOR
    CARD_BG = theme.CARD_BACKGROUND
    TEXT_COLOR = theme.TEXT_COLOR

    def go_deportistas(e):
        show_deportistas(page)

    def go_valoracion(e):
        show_valoracion(page)

    def go_historial(e):
        show_historial(page)

    def card_item(icon, label, on_click=None):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=PRIMARY_COLOR),
                    ft.Container(height=10),
                    ft.Text(label, size=16, weight=ft.FontWeight.W_500, color=TEXT_COLOR, text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            # width removed for responsiveness
            height=150,
            bgcolor=CARD_BG,
            border_radius=15,
            padding=20,
            ink=True,
            on_click=on_click,
            shadow=theme.card_shadow(),
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3}
        )

    # Grid of options
    options_grid = ft.ResponsiveRow(
        [
            card_item(ft.Icons.PERSON_OUTLINE, "Deportistas", on_click=go_deportistas),
            card_item(ft.Icons.MONITOR_WEIGHT_OUTLINED, "Valoración Corporal", on_click=go_valoracion),
            card_item(ft.Icons.TIMELINE, "Historial", on_click=go_historial),
            card_item(ft.Icons.LINK, "Asignaciones"),
            card_item(ft.Icons.SETTINGS_OUTLINED, "Entidades"),
        ],
        spacing=20,
        run_spacing=20,
    )

    return ft.Container(
        content=ft.Column(
            [
                page_header("Dashboard", color=theme.HEADING_COLOR),
                ft.Text("Dashboard", size=16, color=theme.SUBTITLE_COLOR),
                ft.Container(height=20),
                info_banner("Bienvenido al sistema de somatocarta y\nvaloración deportiva."),
                ft.Container(height=30),
                options_grid
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=40,
        bgcolor=BG_COLOR,
        expand=True
    )
