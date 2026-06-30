import flet as ft

from app_config import session_clear, show_snack
from src.frontend import theme
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.components import mobile_top_bar, page_width


SHELL_MOBILE_BREAKPOINT = 900


def open_overlay(page, control):
    try:
        if control not in page.overlay:
            page.overlay.append(control)
        control.open = True
        page.update()
    except Exception:
        page.open(control)


def close_overlay(page, control):
    if control is None:
        return
    try:
        page.close(control)
    except Exception:
        control.open = False
        try:
            control.update()
        except Exception:
            page.update()


def run_after_overlay_close(page, action):
    def execute():
        try:
            action()
        except Exception as error:
            show_snack(page, f"No se pudo abrir la pantalla: {error}")

    if hasattr(page, "run_thread"):
        page.run_thread(execute)
    else:
        execute()


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
                ft.Icon(item["icon"], size=17, color=theme.PRIMARY_COLOR if selected else theme.SUBTITLE_COLOR),
                ft.Text(item["label"], size=12, weight=ft.FontWeight.BOLD if selected else None, color=theme.PRIMARY_COLOR if selected else theme.TEXT_COLOR),
            ],
            spacing=9,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=9),
        bgcolor=theme.INFO_BACKGROUND if selected else ft.Colors.TRANSPARENT,
        border_radius=theme.RADIUS_SMALL,
        ink=True,
        on_click=lambda event: item["action"](),
        width=float("inf") if compact else None,
    )


def perform_logout(page):
    logout_callback = None
    try:
        from src.frontend.navigation import get_logout_callback

        logout_callback = get_logout_callback()
    except Exception:
        logout_callback = None

    if logout_callback:
        logout_callback()
        return
    session_clear(page)
    page.clean()
    page.update()


def build_sidebar(page, active_key):
    items = build_navigation_items(page)

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.HEXAGON_OUTLINED, size=18, color=theme.PRIMARY_COLOR),
                            width=30,
                            height=30,
                            bgcolor=theme.INFO_BACKGROUND,
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text("Somatocarta", size=15, weight=ft.FontWeight.BOLD, color=theme.PRIMARY_COLOR),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=16, color=theme.SURFACE_BORDER),
                *[build_nav_button(item, active_key) for item in items],
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, color=theme.ERROR_COLOR, size=17),
                            ft.Text("Cerrar sesión", color=theme.ERROR_COLOR, size=13, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=9,
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=9),
                    border_radius=theme.RADIUS_SMALL,
                    ink=True,
                    on_click=lambda _: perform_logout(page),
                ),
            ],
            spacing=3,
            expand=True,
        ),
        width=220,
        padding=16,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(right=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )


def build_mobile_menu(page, active_key):
    items = build_navigation_items(page)
    menu_panel = None

    def menu_item(item):
        def navigate(_):
            menu_panel.visible = False
            page.update()
            run_after_overlay_close(page, item["action"])

        return build_nav_button({**item, "action": lambda: navigate(None)}, active_key, compact=True)

    def close_menu(_=None):
        menu_panel.visible = False
        page.update()

    def logout(_=None):
        close_menu()
        run_after_overlay_close(page, lambda: perform_logout(page))

    menu_height = max(520, (getattr(page, "height", 700) or 700) - 16)
    menu_panel = ft.Container(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Menú principal", size=18, weight=ft.FontWeight.BOLD, expand=True),
                            ft.IconButton(ft.Icons.CLOSE, tooltip="Cerrar", on_click=close_menu),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    *[menu_item(item) for item in items],
                    ft.Divider(),
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
                spacing=6,
                scroll=ft.ScrollMode.AUTO,
            ),
            height=menu_height,
            padding=ft.padding.only(left=16, right=16, top=34, bottom=12),
        ),
        visible=False,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(right=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )

    def open_menu(_):
        menu_panel.visible = not menu_panel.visible
        page.update()

    button = ft.IconButton(ft.Icons.MENU, tooltip="Menú", icon_color=theme.PRIMARY_COLOR, on_click=open_menu)
    return button, menu_panel


def build_bottom_navigation(page, active_key, on_more=None):
    from src.frontend import navigation

    items = [
        ("dashboard", "Inicio", ft.Icons.HOME_OUTLINED, lambda: navigation.show_dashboard(page)),
        ("valoracion", "Valoraciones", ft.Icons.MONITOR_WEIGHT_OUTLINED, lambda: navigation.show_valoracion(page)),
        ("deportistas", "Deportistas", ft.Icons.PEOPLE_OUTLINE, lambda: navigation.show_deportistas(page)),
        ("more", "Mas", ft.Icons.MORE_HORIZ, on_more),
    ]

    def tab(key, label, icon, action):
        selected = active_key == key or (
            key == "more"
            and active_key in {"historial", "analisis_longitudinal", "deportes", "entidades", "asignaciones", "acerca"}
        )
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=20, color=theme.PRIMARY_BLUE if selected else theme.MUTED_TEXT_COLOR),
                    ft.Text(label, size=10, color=theme.PRIMARY_BLUE if selected else theme.MUTED_TEXT_COLOR),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            ink=action is not None,
            on_click=lambda _: action() if action else None,
            alignment=ft.alignment.center,
        )

    return ft.Container(
        content=ft.Row([tab(*item) for item in items], spacing=0),
        height=72,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(top=ft.BorderSide(1, theme.SURFACE_BORDER)),
        border_radius=ft.border_radius.only(top_left=18, top_right=18),
        padding=ft.padding.only(left=8, right=8, top=8, bottom=6),
    )


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
            run_after_overlay_close(page, action)

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
                            ft.TextButton("Valorar", on_click=navigate_from_result(lambda athlete_id=identi: navigation.show_valoracion(page, athlete_id))),
                            ft.TextButton("Historial", on_click=navigate_from_result(lambda athlete_id=identi: navigation.show_historial(page, athlete_id))),
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
                modal=False,
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
            open_overlay(page, dialog)
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


def build_app_shell(page, content, active_key="dashboard", title="Somatocarta", actions=None, show_search=True):
    mobile_menu, mobile_navigation_panel = build_mobile_menu(page, active_key)
    mobile_menu_container = ft.Container(
        content=mobile_menu,
        col={"xs": 2, "sm": 1, "md": 1},
        alignment=ft.alignment.center_left,
    )
    search_container = None
    if show_search:
        search_container = ft.Container(
            content=build_global_search(page),
            col={"xs": 12, "sm": 11, "md": 8, "lg": 9},
        )
    actions_container = ft.Container(
        content=ft.Row(
            actions or [],
            spacing=6,
            alignment=ft.MainAxisAlignment.END,
            scroll=ft.ScrollMode.AUTO,
        ),
        col={"xs": 12, "sm": 12, "md": 3, "lg": 3},
        visible=bool(actions),
    )
    top_bar_controls = [mobile_menu_container]
    if search_container is not None:
        top_bar_controls.append(search_container)
    top_bar_controls.append(actions_container)
    top_bar = ft.Container(
        content=ft.ResponsiveRow(
            top_bar_controls,
            spacing=10,
            run_spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.WHITE,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border=ft.border.only(bottom=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )
    main_content = ft.Container(content=content, expand=True, bgcolor=theme.BACKGROUND_COLOR, alignment=ft.alignment.top_center)
    mobile_header = mobile_top_bar(
        title or "Somatocarta",
        on_menu=lambda _: setattr(mobile_navigation_panel, "visible", True) or page.update(),
        on_trailing=lambda _: perform_logout(page),
    )
    bottom_navigation = build_bottom_navigation(
        page,
        active_key,
        on_more=lambda: setattr(mobile_navigation_panel, "visible", True) or page.update(),
    )
    page._somatocarta_mobile_header = mobile_header
    page._somatocarta_bottom_navigation = bottom_navigation
    body = ft.Column([top_bar, mobile_header, mobile_navigation_panel, main_content, bottom_navigation], spacing=0, expand=True)
    sidebar = build_sidebar(page, active_key)
    shell = ft.Container(
        content=ft.Row([sidebar, body], spacing=0, expand=True),
        expand=True,
        bgcolor=theme.BACKGROUND_COLOR,
    )

    previous_resize_handler = getattr(page, "on_resized", None)

    def update_shell_layout(event=None, refresh=True):
        is_mobile = page_width(page, default=390) < SHELL_MOBILE_BREAKPOINT
        has_top_bar_content = is_mobile or search_container is not None or bool(actions)
        sidebar.visible = not is_mobile
        mobile_menu_container.visible = is_mobile
        mobile_navigation_panel.visible = mobile_navigation_panel.visible if is_mobile else False
        top_bar.visible = has_top_bar_content and not is_mobile
        mobile_header.visible = is_mobile
        bottom_navigation.visible = is_mobile
        main_content.bgcolor = theme.MOBILE_BACKGROUND if is_mobile else theme.BACKGROUND_COLOR
        if search_container is not None:
            search_container.col = {"xs": 12, "sm": 11, "md": 8, "lg": 9} if is_mobile else {"md": 8, "lg": 9}
        if refresh:
            page.update()

    def handle_resize(event):
        if previous_resize_handler is not None:
            previous_resize_handler(event)
        update_shell_layout(event)

    page.on_resized = handle_resize
    update_shell_layout(refresh=False)
    return shell
