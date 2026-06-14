import threading
import time
import unittest
from unittest.mock import patch

from src.frontend.navigation import get_logout_callback, set_logout_callback, show_dashboard, show_view


class FakePage:
    def __init__(self):
        self.controls = [{"old": "content"}]
        self.session = {}

    def clean(self):
        self.controls.clear()

    def add(self, control):
        self.controls.append(control)


class SlowCleanPage(FakePage):
    def clean(self):
        self.controls.clear()
        time.sleep(0.01)


class NavigationTests(unittest.TestCase):
    def tearDown(self):
        set_logout_callback(None)

    def test_show_view_replaces_current_page_content(self):
        page = FakePage()

        show_view(page, lambda current_page: {"page": current_page})

        self.assertEqual(len(page.controls), 1)
        self.assertEqual(page.controls, [{"page": page}])

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

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}):
            show_dashboard(page)

        self.assertIs(get_logout_callback(), callback)
        self.assertEqual(page.controls, [{"dashboard": True}])

    def test_show_dashboard_updates_logout_callback_when_provided(self):
        page = FakePage()
        callback = object()

        with patch("views.dashboard.DashboardView", return_value={"dashboard": True}):
            show_dashboard(page, callback)

        self.assertIs(get_logout_callback(), callback)


if __name__ == "__main__":
    unittest.main()
