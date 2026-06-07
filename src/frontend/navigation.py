def show_view(page, view_factory):
    page.clean()
    page.add(view_factory(page))


def show_dashboard(page):
    from views.dashboard import DashboardView

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
