import flet as ft

from app_config import show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import page_width


def close_overlay(page, control):
    if control is None:
        return
    try:
        page.close(control)
    except Exception:
        pass
    try:
        control.open = False
    except Exception:
        pass
    overlay = getattr(page, "overlay", None)
    if overlay is not None and control in overlay:
        overlay.remove(control)
    try:
        page.update()
    except Exception:
        pass


def build_navigation_items(page):
    from src.frontend import navigation

    return [
        {"key": "dashboard", "label": "Dashboard", "icon": ft.Icons.DASHBOARD_OUTLINED, "action": lambda: navigation.show_dashboard(page)},
        {"key": "valoracion", "label": "Valoración corporal", "icon": ft.Icons.MONITOR_WEIGHT_OUTLINED, "action": lambda: navigation.show_valoracion(page)},
        {"key": "deportistas", "label": "Deportistas", "icon": ft.Icons.PEOPLE_OUTLINE, "action": lambda: navigation.show_deportistas(page)},
        {"key": "historial", "label": "Análisis de valoración corporal", "icon": ft.Icons.ANALYTICS_OUTLINED, "action": lambda: navigation.show_historial(page)},
        {"key": "analisis_longitudinal", "label": "Análisis longitudinal", "icon": ft.Icons.SHOW_CHART, "action": lambda: navigation.show_analisis_longitudinal(page)},
        {"key": "deportes", "label": "Deportes", "icon": ft.Icons.SPORTS_SOCCER, "action": lambda: navigation.show_deportes(page)},
        {"key": "entidades", "label": "Entidades", "icon": ft.Icons.BUSINESS_OUTLINED, "action": lambda: navigation.show_entidades(page)},
        {"key": "asignaciones", "label": "Asignaciones", "icon": ft.Icons.LINK, "action": lambda: navigation.show_asignaciones(page)},
        {"key": "acerca", "label": "Acerca del proyecto", "icon": ft.Icons.INFO_OUTLINE, "action": lambda: navigation.show_acerca(page)},
    ]


def build_nav_button(item, active_key, compact=False):
    selected = item["key"] == active_key
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(item["icon"], size=20, color=theme.PRIMARY_COLOR if selected else theme.SUBTITLE_COLOR),
                ft.Text(item["label"], size=13, weight=ft.FontWeight.BOLD if selected else None, color=theme.PRIMARY_COLOR if selected else theme.TEXT_COLOR),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        bgcolor=theme.INFO_BACKGROUND if selected else ft.Colors.TRANSPARENT,
        border_radius=theme.RADIUS_SMALL,
        ink=True,
        on_click=lambda event: item["action"](),
        width=float("inf") if compact else None,
    )


def build_sidebar(page, active_key):
    items = build_navigation_items(page)
    logout_callback = None
    try:
        from src.frontend.navigation import get_logout_callback

        logout_callback = get_logout_callback()
    except Exception:
        logout_callback = None

    def logout(_=None):
        if logout_callback:
            logout_callback()
            return
        page.session.clear()
        page.clean()
        page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Somatocarta", size=20, weight=ft.FontWeight.BOLD, color=theme.PRIMARY_COLOR),
                ft.Text("Panel operativo", size=12, color=theme.SUBTITLE_COLOR),
                ft.Divider(height=18),
                *[build_nav_button(item, active_key) for item in items],
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, color=theme.ERROR_COLOR, size=20),
                            ft.Text("Cerrar sesión", color=theme.ERROR_COLOR, size=13, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    border_radius=theme.RADIUS_SMALL,
                    ink=True,
                    on_click=logout,
                ),
            ],
            spacing=4,
            expand=True,
        ),
        width=260,
        padding=18,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(right=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )


def build_mobile_menu(page, active_key):
    items = build_navigation_items(page)
    dialog = None

    def menu_item(item):
        def navigate(_):
            close_overlay(page, dialog)
            item["action"]()

        return build_nav_button({**item, "action": lambda: navigate(None)}, active_key, compact=True)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Menú principal"),
        content=ft.Container(
            content=ft.Column([menu_item(item) for item in items], spacing=6),
            width=360,
        ),
    )

    def open_menu(_):
        page.open(dialog)

    return ft.IconButton(ft.Icons.MENU, tooltip="Menú", icon_color=theme.PRIMARY_COLOR, on_click=open_menu)


def build_global_search(page):
    api = ApiClient(page)
    active_dialog = {"control": None}
    search_field = ft.TextField(
        hint_text="Buscar deportista por nombre o ID",
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        expand=True,
    )

    def close_search_dialog(_=None):
        close_overlay(page, active_dialog.get("control"))
        active_dialog["control"] = None

    def navigate_from_result(action):
        def handler(_):
            close_search_dialog()
            action()

        return handler

    def render_results(items):
        controls = []
        from src.frontend import navigation

        for athlete in items[:5]:
            name = athlete.get("NOMBRE_DEPORTISTA") or "Deportista"
            identi = athlete.get("IDENTI_DEPORTISTA") or ""
            controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON_OUTLINE, color=theme.PRIMARY_COLOR),
                            ft.Column(
                                [
                                    ft.Text(name, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"ID: {identi}", size=12, color=theme.SUBTITLE_COLOR),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.TextButton("Valorar", on_click=navigate_from_result(lambda: navigation.show_valoracion(page))),
                            ft.TextButton("Historial", on_click=navigate_from_result(lambda: navigation.show_historial(page))),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=10,
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    border_radius=theme.RADIUS_SMALL,
                )
            )
        if not controls:
            controls.append(ft.Text("Sin resultados.", color=theme.SUBTITLE_COLOR))
        return controls

    def submit(_=None):
        query = (search_field.value or "").strip()
        if not query:
            show_snack(page, "Escribe un nombre o ID para buscar.")
            return
        try:
            result = api.list_deportistas_page(query, page=1, page_size=5)
            items = result.get("items", []) if isinstance(result, dict) else result
            content_height = min(360, max(120, (len(items[:5]) or 1) * 72 + 24))
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    [
                        ft.Text(f"Resultados para: {query}", expand=True),
                        ft.IconButton(ft.Icons.CLOSE, tooltip="Cerrar", on_click=close_search_dialog),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                content=ft.Container(content=ft.Column(render_results(items), spacing=8, scroll=ft.ScrollMode.AUTO), width=620, height=content_height),
                actions=[ft.TextButton("Cerrar", on_click=close_search_dialog)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            active_dialog["control"] = dialog
            page.open(dialog)
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as error:
            show_snack(page, f"No se pudo buscar: {error}")

    search_field.on_submit = submit
    return ft.Container(
        content=ft.Row(
            [
                search_field,
                ft.IconButton(ft.Icons.SEARCH, icon_color=theme.PRIMARY_COLOR, tooltip="Buscar", on_click=submit),
            ],
            spacing=4,
        ),
        expand=True,
    )


def build_app_shell(page, content, active_key="dashboard", title="Somatocarta", actions=None):
    is_mobile = page_width(page) < 900
    top_bar = ft.Container(
        content=ft.Row(
            [
                build_mobile_menu(page, active_key) if is_mobile else ft.Container(visible=False),
                ft.Column(
                    [
                        ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                        ft.Text("Panel operativo de Somatocarta", size=12, color=theme.SUBTITLE_COLOR),
                    ],
                    spacing=2,
                ),
                ft.Container(width=12),
                build_global_search(page),
                *(actions or []),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.WHITE,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border=ft.border.only(bottom=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )
    main_content = ft.Container(content=content, expand=True, bgcolor=theme.BACKGROUND_COLOR)
    body = ft.Column([top_bar, main_content], spacing=0, expand=True)
    if is_mobile:
        return ft.Container(content=body, expand=True, bgcolor=theme.BACKGROUND_COLOR)
    return ft.Container(
        content=ft.Row([build_sidebar(page, active_key), body], spacing=0, expand=True),
        expand=True,
        bgcolor=theme.BACKGROUND_COLOR,
    )
