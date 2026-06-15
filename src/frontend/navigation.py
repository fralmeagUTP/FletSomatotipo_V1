from threading import Lock


_logout_callback = None
_view_lock = Lock()


def set_logout_callback(callback):
    global _logout_callback
    _logout_callback = callback


def get_logout_callback():
    return _logout_callback


def show_view(page, view_factory, active_key=None, title=None):
    view = view_factory(page)
    if active_key:
        from src.frontend.app_shell import build_app_shell

        view = build_app_shell(page, view, active_key=active_key, title=title or "Somatocarta")
    with _view_lock:
        page.clean()
        page.add(view)


def show_dashboard(page, logout_callback=None):
    from views.dashboard import DashboardView

    if logout_callback is not None:
        set_logout_callback(logout_callback)
    show_view(page, DashboardView, active_key="dashboard", title="Dashboard")


def show_deportistas(page):
    from views.deportistas import DeportistasView

    show_view(page, DeportistasView, active_key="deportistas", title="Deportistas")


def show_valoracion(page):
    from views.valoracion import ValoracionView

    show_view(page, ValoracionView, active_key="valoracion", title="Valoración corporal")


def show_historial(page):
    from views.historial import HistorialView

    show_view(page, HistorialView, active_key="historial", title="Análisis de valoración corporal")


def show_analisis_longitudinal(page):
    from views.analisis_longitudinal import AnalisisLongitudinalView

    show_view(page, AnalisisLongitudinalView, active_key="analisis_longitudinal", title="Análisis longitudinal")


def show_entidades(page):
    from views.entidades import EntidadesView

    show_view(page, EntidadesView, active_key="entidades", title="Entidades")


def show_deportes(page):
    from views.deportes import DeportesView

    show_view(page, DeportesView, active_key="deportes", title="Deportes")


def show_asignaciones(page):
    from views.asignaciones import AsignacionesView

    show_view(page, AsignacionesView, active_key="asignaciones", title="Asignaciones")


def show_acerca(page):
    from views.acerca import AcercaView

    show_view(page, AcercaView, active_key="acerca", title="Acerca del proyecto")
