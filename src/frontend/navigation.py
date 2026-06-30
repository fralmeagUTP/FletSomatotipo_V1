import inspect
from threading import Lock

import flet as ft


_logout_callback = None
_view_lock = Lock()
def set_logout_callback(callback):
    global _logout_callback
    _logout_callback = callback


def get_logout_callback():
    return _logout_callback


def _configure_route_handler(page):
    if getattr(page, "_somatocarta_route_handler", None) is not None:
        return

    previous_handler = getattr(page, "on_route_change", None)
    page._somatocarta_route_renderers = {}

    def handle_route_change(event):
        route = getattr(event, "route", None) or getattr(page, "route", None)
        if route == getattr(page, "_somatocarta_active_route", None):
            return
        renderer = page._somatocarta_route_renderers.get(route)
        if renderer is not None:
            renderer()
        elif callable(previous_handler):
            previous_handler(event)

    page.on_route_change = handle_route_change
    page._somatocarta_route_handler = handle_route_change


def _configure_android_back_handler(page):
    if getattr(page, "_somatocarta_view_pop_handler", None) is not None:
        return

    previous_handler = getattr(page, "on_view_pop", None)

    async def handle_view_pop(event):
        local_handler = getattr(page, "_somatocarta_local_back_handler", None)
        if callable(local_handler) and local_handler():
            page.update()
            return

        views = getattr(page, "views", None)
        if views is not None and len(views) > 1:
            popped_view = getattr(event, "view", None)
            if popped_view in views:
                views.remove(popped_view)
            else:
                views.pop()
            previous_view = views[-1]
            page._somatocarta_active_route = previous_view.route
            page.on_resized = (previous_view.data or {}).get("resize_handler")
            await page.push_route(previous_view.route)
            page.update()
            return

        if views is not None and len(views) == 1:
            window = getattr(page, "window", None)
            close_window = getattr(window, "close", None)
            if callable(close_window):
                result = close_window()
                if inspect.isawaitable(result):
                    await result
                return

        if callable(previous_handler):
            result = previous_handler(event)
            if inspect.isawaitable(result):
                await result

    page.on_view_pop = handle_view_pop
    page._somatocarta_view_pop_handler = handle_view_pop

async def _push_route(page, route):
    await page.push_route(route)


def show_login_view(page, content):
    page._somatocarta_active_route = "/login"
    page._somatocarta_local_back_handler = None
    renderers = getattr(page, "_somatocarta_route_renderers", None)
    if renderers is not None:
        renderers.clear()

    views = getattr(page, "views", None)
    page.clean()
    if views is None:
        page.add(content)
        page.update()
        return

    views.clear()
    views.append(
        ft.View(
            route="/login",
            controls=[content],
            padding=0,
            bgcolor=ft.Colors.WHITE,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            can_pop=True,
        )
    )
    page.update()
    if hasattr(page, "navigate"):
        page.navigate("/login")


def show_view(page, view_factory, active_key=None, title=None, show_search=True, route=None, record_history=True):
    pending_route = None
    if route:
        _configure_route_handler(page)
        _configure_android_back_handler(page)
        page._somatocarta_route_renderers[route] = lambda: show_view(
            page,
            view_factory,
            active_key=active_key,
            title=title,
            show_search=show_search,
            route=route,
            record_history=False,
        )
        if record_history and hasattr(page, "push_route") and getattr(page, "route", None) != route:
            pending_route = route

    page.on_resized = None
    rendered = view_factory(page)
    after_render = None
    if isinstance(rendered, tuple) and len(rendered) == 2 and callable(rendered[1]):
        view, after_render = rendered
    else:
        view = rendered
    if active_key:
        from src.frontend.app_shell import build_app_shell

        view = build_app_shell(
            page,
            view,
            active_key=active_key,
            title=title or "Somatocarta",
            show_search=show_search,
        )
    page._somatocarta_local_back_handler = None
    views = getattr(page, "views", None)
    if route and views is not None:
        page_view = ft.View(
            route=route,
            controls=[view],
            padding=0,
            bgcolor=getattr(page, "bgcolor", None),
            can_pop=True,
            data={"resize_handler": getattr(page, "on_resized", None)},
        )
        with _view_lock:
            page.clean()
            existing_index = next((index for index, item in enumerate(views) if item.route == route), None)
            if not record_history and existing_index is not None:
                del views[existing_index + 1 :]
            elif record_history:
                views.append(page_view)
            elif existing_index is None:
                views.append(page_view)
        page.update()
    else:
        with _view_lock:
            page.clean()
            page.add(view)
    if route:
        page._somatocarta_active_route = route
    if after_render is not None:
        if hasattr(page, "run_thread"):
            page.run_thread(after_render)
        else:
            after_render()
    if pending_route:
        if inspect.iscoroutinefunction(page.push_route):
            page.run_task(_push_route, page, pending_route)
        else:
            page.push_route(pending_route)


def show_dashboard(page, logout_callback=None):
    from views.dashboard import DashboardView

    if logout_callback is not None:
        set_logout_callback(logout_callback)
    show_view(page, DashboardView, active_key="dashboard", title="Dashboard", show_search=False, route="/dashboard")


def show_deportistas(page):
    from views.deportistas import DeportistasView

    show_view(page, DeportistasView, active_key="deportistas", title="Deportistas", show_search=False, route="/deportistas")


def show_valoracion(page, initial_query=None):
    from views.valoracion import ValoracionView

    show_view(
        page,
        lambda current_page: ValoracionView(current_page, initial_query),
        active_key="valoracion",
        title="Valoración corporal",
        show_search=False,
        route="/valoracion",
    )


def show_historial(page, initial_query=None):
    from views.historial import HistorialView

    show_view(
        page,
        lambda current_page: HistorialView(current_page, initial_query),
        active_key="historial",
        title="Análisis de valoración corporal",
        show_search=False,
        route="/historial",
    )


def show_analisis_longitudinal(page):
    from views.analisis_longitudinal import AnalisisLongitudinalView

    show_view(
        page,
        AnalisisLongitudinalView,
        active_key="analisis_longitudinal",
        title="Análisis longitudinal",
        show_search=False,
        route="/analisis-longitudinal",
    )


def show_entidades(page):
    from views.entidades import EntidadesView

    show_view(page, EntidadesView, active_key="entidades", title="Entidades", show_search=False, route="/entidades")


def show_deportes(page):
    from views.deportes import DeportesView

    show_view(page, DeportesView, active_key="deportes", title="Deportes", show_search=False, route="/deportes")


def show_asignaciones(page):
    from views.asignaciones import AsignacionesView

    show_view(page, AsignacionesView, active_key="asignaciones", title="Asignaciones", show_search=False, route="/asignaciones")


def show_acerca(page):
    from views.acerca import AcercaView

    show_view(page, AcercaView, active_key="acerca", title="Acerca del proyecto", show_search=False, route="/acerca")
