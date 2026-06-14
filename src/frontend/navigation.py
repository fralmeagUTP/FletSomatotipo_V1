from threading import Lock


_logout_callback = None
_view_lock = Lock()


def set_logout_callback(callback):
    global _logout_callback
    _logout_callback = callback


def get_logout_callback():
    return _logout_callback


def show_view(page, view_factory):
    view = view_factory(page)
    with _view_lock:
        page.clean()
        page.add(view)


def show_dashboard(page, logout_callback=None):
    from views.dashboard import DashboardView

    if logout_callback is not None:
        set_logout_callback(logout_callback)
    show_view(page, DashboardView)


def show_deportistas(page):
    from views.deportistas import DeportistasView

    show_view(page, DeportistasView)


def show_valoracion(page):
    from views.valoracion import ValoracionView

    show_view(page, ValoracionView)


def show_historial(page):
    from views.historial import HistorialView

    show_view(page, HistorialView)


def show_entidades(page):
    from views.entidades import EntidadesView

    show_view(page, EntidadesView)


def show_deportes(page):
    from views.deportes import DeportesView

    show_view(page, DeportesView)


def show_asignaciones(page):
    from views.asignaciones import AsignacionesView

    show_view(page, AsignacionesView)
