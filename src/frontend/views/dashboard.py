import flet as ft

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
    PRIMARY_COLOR = "#2e5cb8"
    BG_COLOR = "#f5f7fb" # Light blueish grey background seen in image
    CARD_BG = ft.Colors.WHITE
    TEXT_COLOR = "#333333"

    def go_deportistas(e):
        from .deportistas import DeportistasView
        page.clean()
        page.add(DeportistasView(page))

    def go_valoracion(e):
        from .valoracion import ValoracionView
        page.clean()
        page.add(ValoracionView(page))

    def go_historial(e):
        from .historial import HistorialView
        page.clean()
        page.add(HistorialView(page))

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
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.BLUE_GREY_50,
                offset=ft.Offset(0, 5),
            ),
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3}
        )

    # Info Banner
    info_banner = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY_COLOR, size=30),
                ft.Container(width=15),
                ft.Text(
                    "Bienvenido al sistema de somatocarta y\nvaloración deportiva.",
                    size=16,
                    color=TEXT_COLOR
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor="#e8f0fe", # Light blue background matching image
        padding=20,
        border_radius=10,
        width=float("inf") # Full width
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
                ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD, color="#1a1a1a"),
                ft.Text("Dashboard", size=16, color="#666666"), # Breadcrumb style
                ft.Container(height=20),
                info_banner,
                ft.Container(height=30),
                options_grid
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=40,
        bgcolor=BG_COLOR,
        expand=True
    )
