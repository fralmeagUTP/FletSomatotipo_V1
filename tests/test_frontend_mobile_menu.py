import unittest
from unittest.mock import patch

from src.frontend.app_shell import build_mobile_menu


class FakePage:
    def __init__(self):
        self.height = 700
        self.thread_callbacks = []
        self.update_count = 0

    def update(self):
        self.update_count += 1

    def run_thread(self, callback):
        self.thread_callbacks.append(callback)


class MobileMenuTests(unittest.TestCase):
    def test_menu_closes_before_deferred_navigation(self):
        page = FakePage()
        menu_button, menu_panel = build_mobile_menu(page, "dashboard")
        menu_button.on_click(None)
        dashboard_item = menu_panel.content.content.controls[1]

        with patch("src.frontend.navigation.show_dashboard") as navigate:
            dashboard_item.on_click(None)

            self.assertFalse(menu_panel.visible)
            navigate.assert_not_called()

            page.thread_callbacks.pop(0)()

        navigate.assert_called_once_with(page)

    def test_menu_is_scrollable_and_includes_logout(self):
        page = FakePage()
        menu_button, menu_panel = build_mobile_menu(page, "dashboard")
        menu_button.on_click(None)
        menu_column = menu_panel.content.content
        logout_item = menu_column.controls[-1]

        self.assertTrue(menu_panel.visible)
        self.assertIsNotNone(menu_column.scroll)
        self.assertEqual(logout_item.content.controls[1].value, "Cerrar sesión")


if __name__ == "__main__":
    unittest.main()
