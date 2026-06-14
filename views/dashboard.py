import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.assets import MODULE_IMAGES, asset_path
from src.frontend.components import info_banner, responsive_padding
from src.frontend.navigation import (
    get_logout_callback,
    show_asignaciones,
    show_deportes,
    show_deportistas,
    show_entidades,
    show_historial,
    show_valoracion,
)


def DashboardView(page: ft.Page):
    """
    Vista principal con acceso a módulos y métricas operativas básicas.
    """
    primary_color = theme.PRIMARY_COLOR
    bg_color = theme.BACKGROUND_COLOR
    card_bg = theme.CARD_BACKGROUND
    text_color = theme.TEXT_COLOR
    api = ApiClient(page)

    # Get user info from session
    username = page.session.get("username") or "Usuario"
    login_user = page.session.get("login_user") or ""
    
    # Get logout callback from navigation module
    logout_callback = get_logout_callback()

    summary = {
        "total_deportistas": "-",
        "total_valoraciones": "-",
        "vista_contrato": {"ok": False, "missing": []},
    }

    try:
        summary.update(api.get_dashboard_summary() or {})
    except ApiError as error:
        show_snack(page, f"No se pudieron cargar las métricas: {error}")

    def go_deportistas(_):
        show_deportistas(page)

    def go_valoracion(_):
        show_valoracion(page)

    def go_historial(_):
        show_historial(page)

    def go_entidades(_):
        show_entidades(page)

    def go_deportes(_):
        show_deportes(page)

    def go_asignaciones(_):
        show_asignaciones(page)

    def handle_logout(_):
        if logout_callback:
            logout_callback()
            return
        page.session.clear()
        page.clean()
        page.update()

    def card_item(icon, label, on_click=None, image_name=None):
        visual = (
            ft.Image(src=asset_path(image_name), height=64, fit=ft.ImageFit.CONTAIN)
            if image_name
            else ft.Icon(icon, size=36, color=primary_color)
        )
        return ft.Container(
            content=ft.Column(
                [
                    visual,
                    ft.Container(height=8),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=140,
            bgcolor=card_bg,
            border_radius=15,
            padding=16,
            ink=True,
            on_click=on_click,
            shadow=theme.card_shadow(),
            col={"xs": 6, "sm": 4, "md": 4, "lg": 2},
        )

    def metric_card(title, value, subtitle, icon, color=primary_color):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color, size=30),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(title, size=12, color=theme.SUBTITLE_COLOR),
                            ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=text_color),
                            ft.Text(subtitle, size=11, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=2,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=card_bg,
            border_radius=12,
            padding=16,
            shadow=theme.card_shadow(),
            col={"xs": 12, "sm": 4, "md": 4},
        )

    view_contract = summary.get("vista_contrato") or {}
    missing_columns = view_contract.get("missing") or []
    view_ok = bool(view_contract.get("ok"))
    view_status = "OK" if view_ok else "Revisar"
    view_subtitle = "Contrato completo" if view_ok else f"Faltan {len(missing_columns)} columnas"

    # Header with user info and logout
    header_section = ft.Container(
        content=ft.Row(
            [
                # Left side - Title
                ft.Column(
                    [
                        ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                        ft.Text("Resumen operativo", size=14, color=theme.SUBTITLE_COLOR),
                    ],
                    spacing=4,
                ),
                ft.Container(expand=True),
                # Right side - User info and logout
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Sesión activa", size=11, color=theme.SUBTITLE_COLOR),
                                ft.Text(
                                    f"👤 {username}" if username != "Usuario" else " Usuario",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=text_color,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        ),
                        ft.Container(width=16),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Cerrar sesión",
                            on_click=handle_logout,
                            style=ft.ButtonStyle(
                                color=theme.ERROR_COLOR,
                                bgcolor=ft.Colors.RED_50,
                            ),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=card_bg,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        border_radius=12,
        shadow=theme.card_shadow(),
    )

    metrics_grid = ft.ResponsiveRow(
        [
            metric_card(
                "Deportistas",
                summary.get("total_deportistas", "-"),
                "Registros activos en base de datos",
                ft.Icons.PEOPLE_OUTLINE,
            ),
            metric_card(
                "Valoraciones",
                summary.get("total_valoraciones", "-"),
                "Mediciones registradas",
                ft.Icons.MONITOR_WEIGHT_OUTLINED,
            ),
            metric_card(
                "Vista SQL",
                view_status,
                view_subtitle,
                ft.Icons.FACT_CHECK_OUTLINED,
                color=theme.SUCCESS_COLOR if view_ok else theme.ERROR_COLOR,
            ),
        ],
        spacing=16,
        run_spacing=16,
    )

    options_grid = ft.ResponsiveRow(
        [
            card_item(ft.Icons.PERSON_OUTLINE, "Deportistas", on_click=go_deportistas, image_name=MODULE_IMAGES["deportistas"]),
            card_item(ft.Icons.MONITOR_WEIGHT_OUTLINED, "Valoración Corporal", on_click=go_valoracion, image_name=MODULE_IMAGES["valoracion"]),
            card_item(ft.Icons.TIMELINE, "Historial", on_click=go_historial, image_name=MODULE_IMAGES["historial"]),
            card_item(ft.Icons.SPORTS_SOCCER, "Deportes", on_click=go_deportes, image_name=MODULE_IMAGES["deportes"]),
            card_item(ft.Icons.LINK, "Asignaciones", on_click=go_asignaciones, image_name=MODULE_IMAGES["asignaciones"]),
            card_item(ft.Icons.BUSINESS_OUTLINED, "Entidades", on_click=go_entidades, image_name=MODULE_IMAGES["entidades"]),
        ],
        spacing=20,
        run_spacing=20,
    )

    return ft.Container(
        content=ft.Column(
            [
                header_section,
                ft.Container(height=20),
                info_banner("Bienvenido al sistema de somatocarta y valoración deportiva."),
                ft.Container(height=24),
                metrics_grid,
                ft.Container(height=28),
                ft.Text("Módulos del sistema", size=16, weight=ft.FontWeight.W_500, color=theme.HEADING_COLOR),
                ft.Container(height=12),
                options_grid,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=responsive_padding(page),
        bgcolor=bg_color,
        expand=True,
    )
