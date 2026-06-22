import flet as ft

from app_config import session_get, show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import content_card, primary_button, responsive_padding, secondary_button
from src.frontend.navigation import (
    show_acerca,
    show_asignaciones,
    show_analisis_longitudinal,
    show_deportes,
    show_deportistas,
    show_entidades,
    show_historial,
    show_valoracion,
)


def DashboardView(page: ft.Page):
    api = ApiClient(page)
    username = session_get(page, "username") or "Usuario"
    summary = {
        "total_deportistas": "-",
        "total_valoraciones": "-",
        "total_deportes": "-",
        "total_entidades": "-",
        "total_asignaciones": "-",
        "vista_contrato": {"ok": False, "missing": []},
    }

    try:
        summary.update(api.get_dashboard_summary() or {})
    except ApiError as error:
        show_snack(page, f"No se pudieron cargar las métricas: {error}")

    def metric_card(title, value, subtitle, icon, color=theme.PRIMARY_COLOR):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=26, color=color),
                        width=48,
                        height=48,
                        bgcolor=theme.INFO_BACKGROUND if color == theme.PRIMARY_COLOR else ft.Colors.GREEN_50,
                        border_radius=14,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=12, color=theme.SUBTITLE_COLOR),
                            ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                            ft.Text(subtitle, size=11, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_LARGE,
            padding=16,
            shadow=theme.card_shadow(),
            col={"xs": 12, "sm": 6, "lg": 3},
        )

    def module_card(label, description, icon, action):
        visual = ft.Container(
            content=ft.Icon(icon, size=28, color=theme.PRIMARY_COLOR),
            width=48,
            height=48,
            bgcolor=theme.INFO_BACKGROUND,
            border_radius=theme.RADIUS_SMALL,
            alignment=ft.alignment.center,
        )
        return ft.Container(
            content=ft.Row(
                [
                    visual,
                    ft.Column(
                        [
                            ft.Text(label, size=14, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                            ft.Text(description, size=11, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=theme.SUBTITLE_COLOR),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=14,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            border_radius=theme.RADIUS_MEDIUM,
            ink=True,
            on_click=lambda event: action(page),
        )

    def module_group(title, subtitle, modules):
        return content_card(
            ft.Column(
                [
                    ft.Text(title, size=17, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                    ft.Text(subtitle, size=12, color=theme.SUBTITLE_COLOR),
                    ft.ResponsiveRow(
                        [
                            ft.Container(module_card(*module), col={"xs": 12, "md": 6})
                            for module in modules
                        ],
                        spacing=12,
                        run_spacing=12,
                    ),
                ],
                spacing=12,
            ),
            padding=18,
        )

    view_contract = summary.get("vista_contrato") or {}
    view_ok = bool(view_contract.get("ok"))
    missing_columns = view_contract.get("missing") or []
    system_status = "Operativo" if view_ok else "Revisar"
    system_subtitle = "Base de datos lista" if view_ok else f"Faltan {len(missing_columns)} columnas"

    hero = content_card(
        ft.ResponsiveRow(
            [
                ft.Container(
                    ft.Column(
                        [
                            ft.Text(f"Hola, {username}", size=13, color=theme.SUBTITLE_COLOR),
                            ft.Text("Panel operativo Somatocarta", size=28, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                            ft.Text(
                                "Accede rápidamente a valoraciones, análisis, deportistas y administración del sistema.",
                                size=14,
                                color=theme.SUBTITLE_COLOR,
                            ),
                            ft.Row(
                                [
                                    primary_button("Nueva valoración", icon=ft.Icons.ADD, on_click=lambda event: show_valoracion(page)),
                                    secondary_button("Ver análisis", icon=ft.Icons.ANALYTICS_OUTLINED, on_click=lambda event: show_historial(page)),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    col={"xs": 12, "lg": 8},
                ),
                ft.Container(
                    ft.Column(
                        [
                            ft.Text("Acciones rápidas", size=13, color=theme.SUBTITLE_COLOR),
                            ft.Text("Nueva valoración", size=20, weight=ft.FontWeight.BOLD, color=theme.PRIMARY_COLOR),
                            ft.Text("Registra una medición corporal desde el flujo principal.", size=12, color=theme.SUBTITLE_COLOR),
                        ],
                        spacing=6,
                    ),
                    bgcolor=theme.INFO_BACKGROUND,
                    padding=18,
                    border_radius=theme.RADIUS_LARGE,
                    col={"xs": 12, "lg": 4},
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            run_spacing=16,
        ),
        padding=22,
    )

    metrics = ft.ResponsiveRow(
        [
            metric_card("Deportistas", summary.get("total_deportistas", "-"), "Registros activos", ft.Icons.PEOPLE_OUTLINE),
            metric_card("Valoraciones", summary.get("total_valoraciones", "-"), "Mediciones registradas", ft.Icons.MONITOR_WEIGHT_OUTLINED),
            metric_card("Asignaciones", summary.get("total_asignaciones", "-"), "Relaciones deporte-entidad", ft.Icons.LINK),
            metric_card("Sistema", system_status, system_subtitle, ft.Icons.STORAGE, color=theme.SUCCESS_COLOR if view_ok else theme.ERROR_COLOR),
        ],
        spacing=14,
        run_spacing=14,
    )

    operation_modules = [
        ("Valoración corporal", "Registrar una nueva medición", ft.Icons.MONITOR_WEIGHT_OUTLINED, show_valoracion),
        ("Análisis de valoración corporal", "Consultar resultados y PDF individual", ft.Icons.ANALYTICS_OUTLINED, show_historial),
        ("Análisis longitudinal", "Revisar evolución temporal", ft.Icons.SHOW_CHART, show_analisis_longitudinal),
    ]
    management_modules = [
        ("Deportistas", "Crear y administrar deportistas", ft.Icons.PEOPLE_OUTLINE, show_deportistas),
        ("Deportes", "Gestionar catálogo deportivo", ft.Icons.SPORTS_SOCCER, show_deportes),
        ("Entidades", "Administrar instituciones", ft.Icons.BUSINESS_OUTLINED, show_entidades),
        ("Asignaciones", "Relacionar deportistas, deportes y entidades", ft.Icons.LINK, show_asignaciones),
    ]
    system_modules = [
        ("Acerca del proyecto", "Información del alcance y soporte", ft.Icons.INFO_OUTLINE, show_acerca),
    ]

    return ft.Container(
        content=ft.Column(
            [
                hero,
                metrics,
                module_group("Operación y análisis", "Flujos principales del trabajo antropométrico.", operation_modules),
                module_group("Gestión de datos", "Módulos administrativos y catálogos.", management_modules),
                module_group("Sistema", "Información general del proyecto y estado operativo.", system_modules),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=responsive_padding(page),
        bgcolor=theme.BACKGROUND_COLOR,
        expand=True,
    )
