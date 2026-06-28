import asyncio
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.frontend.navigation import (
    get_logout_callback,
    set_logout_callback,
    show_asignaciones,
    show_dashboard,
    show_deportes,
    show_deportistas,
    show_entidades,
    show_historial,
    show_analisis_longitudinal,
    show_valoracion,
    show_view,
)


class FakePage:
    def __init__(self):
        self.controls = [{"old": "content"}]
        self.session = {}
        self.width = 1200
        self.on_resized = lambda event: None

    def clean(self):
        self.controls.clear()

    def add(self, control):
        self.controls.append(control)


class SlowCleanPage(FakePage):
    def clean(self):
        self.controls.clear()
        time.sleep(0.01)


class RoutePage(FakePage):
    def __init__(self):
        super().__init__()
        self.route = "/"
        self.on_route_change = None
        self.pushed_routes = []

    def push_route(self, route):
        self.route = route
        self.pushed_routes.append(route)
        self.on_route_change(SimpleNamespace(route=route))


class AsyncRoutePage(RoutePage):
    async def push_route(self, route):
        self.route = route
        self.pushed_routes.append(route)
        self.on_route_change(SimpleNamespace(route=route))

    def run_task(self, handler, *args):
        asyncio.run(handler(*args))


class NavigationTests(unittest.TestCase):
    def tearDown(self):
        set_logout_callback(None)

    def test_show_view_replaces_current_page_content(self):
        page = FakePage()

        show_view(page, lambda current_page: {"page": current_page})

        self.assertEqual(len(page.controls), 1)
        self.assertEqual(page.controls, [{"page": page}])

    def test_show_view_clears_previous_resize_handler_before_building_view(self):
        page = FakePage()
        resize_handler_seen_by_factory = []

        show_view(page, lambda current_page: resize_handler_seen_by_factory.append(current_page.on_resized) or {})

        self.assertEqual(resize_handler_seen_by_factory, [None])

    def test_show_view_runs_post_render_callback_after_adding_control(self):
        page = FakePage()
        callback_observations = []

        show_view(
            page,
            lambda current_page: (
                {"view": True},
                lambda: callback_observations.append(list(current_page.controls)),
            ),
        )

        self.assertEqual(callback_observations, [[{"view": True}]])

    def test_show_view_does_not_duplicate_controls_when_called_concurrently(self):
        page = SlowCleanPage()
        start = threading.Barrier(2)

        def render(label):
            start.wait()
            show_view(page, lambda current_page: {"view": label, "page": current_page})

        threads = [
            threading.Thread(target=render, args=("first",)),
            threading.Thread(target=render, args=("second",)),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(len(page.controls), 1)

    def test_show_dashboard_preserves_existing_logout_callback_when_not_provided(self):
        page = FakePage()
        callback = object()
        set_logout_callback(callback)

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}), patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": True},
        ) as shell:
            show_dashboard(page)

        self.assertIs(get_logout_callback(), callback)
        self.assertEqual(page.controls, [{"shell": True}])
        self.assertFalse(shell.call_args.kwargs["show_search"])

    def test_show_dashboard_updates_logout_callback_when_provided(self):
        page = FakePage()
        callback = object()

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}), patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": True},
        ):
            show_dashboard(page, callback)

        self.assertIs(get_logout_callback(), callback)

    def test_show_valoracion_passes_initial_athlete_query(self):
        page = FakePage()

        with patch("views.valoracion.ValoracionView", return_value={"valoracion": True}) as view, patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": "valoracion"},
        ) as shell:
            show_valoracion(page, "10025735")

        view.assert_called_once_with(page, "10025735")
        self.assertFalse(shell.call_args.kwargs["show_search"])
        self.assertEqual(page.controls, [{"shell": "valoracion"}])

    def test_show_historial_passes_initial_athlete_query(self):
        page = FakePage()

        with patch("views.historial.HistorialView", return_value={"historial": True}) as view, patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": "historial"},
        ) as shell:
            show_historial(page, "10025735")

        view.assert_called_once_with(page, "10025735")
        self.assertFalse(shell.call_args.kwargs["show_search"])
        self.assertEqual(page.controls, [{"shell": "historial"}])

    def test_show_analisis_longitudinal_hides_global_search(self):
        page = FakePage()

        with patch("views.analisis_longitudinal.AnalisisLongitudinalView", return_value={"longitudinal": True}), patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": "longitudinal"},
        ) as shell:
            show_analisis_longitudinal(page)

        self.assertFalse(shell.call_args.kwargs["show_search"])

    def test_catalog_and_management_views_hide_global_search(self):
        page = FakePage()
        cases = [
            (show_deportistas, "views.deportistas.DeportistasView"),
            (show_deportes, "views.deportes.DeportesView"),
            (show_entidades, "views.entidades.EntidadesView"),
            (show_asignaciones, "views.asignaciones.AsignacionesView"),
        ]

        for navigate, view_path in cases:
            with self.subTest(view=view_path), patch(view_path, return_value={"view": True}), patch(
                "src.frontend.app_shell.build_app_shell",
                return_value={"shell": True},
            ) as shell:
                navigate(page)

            self.assertFalse(shell.call_args.kwargs["show_search"])

    def test_show_acerca_renders_in_global_shell(self):
        from src.frontend.navigation import show_acerca

        page = FakePage()

        with patch("views.acerca.AcercaView", return_value={"acerca": True}), patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": "acerca"},
        ) as shell:
            show_acerca(page)

        self.assertEqual(page.controls, [{"shell": "acerca"}])
        self.assertFalse(shell.call_args.kwargs["show_search"])

    def test_android_back_route_restores_previous_screen(self):
        page = RoutePage()

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}), patch(
            "views.deportistas.DeportistasView", return_value={"deportistas": True}
        ), patch(
            "src.frontend.app_shell.build_app_shell",
            side_effect=lambda page, content, **kwargs: {"shell": kwargs["active_key"]},
        ):
            show_dashboard(page)
            show_deportistas(page)

            self.assertEqual(page.controls, [{"shell": "deportistas"}])
            self.assertEqual(page.pushed_routes, ["/dashboard", "/deportistas"])

            page.route = "/dashboard"
            page.on_route_change(SimpleNamespace(route="/dashboard"))

        self.assertEqual(page.controls, [{"shell": "dashboard"}])

    def test_async_push_route_renders_dashboard_without_unawaited_coroutine(self):
        page = AsyncRoutePage()

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}), patch(
            "src.frontend.app_shell.build_app_shell",
            return_value={"shell": "dashboard"},
        ):
            show_dashboard(page)

        self.assertEqual(page.controls, [{"shell": "dashboard"}])
        self.assertEqual(page.pushed_routes, ["/dashboard"])



if __name__ == "__main__":
    unittest.main()
