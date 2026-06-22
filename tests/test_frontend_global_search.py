import unittest
from unittest.mock import patch

from src.frontend.api_client import ApiClient
from src.frontend.app_shell import build_global_search


class FakeSession:
    def get(self, key):
        return None


class FakePage:
    def __init__(self):
        self.session = FakeSession()
        self.opened = []
        self.closed = []
        self.thread_callbacks = []

    def open(self, control):
        control.open = True
        self.opened.append(control)

    def close(self, control):
        control.open = False
        self.closed.append(control)

    def run_thread(self, callback):
        self.thread_callbacks.append(callback)

    def update(self):
        pass


class GlobalSearchTests(unittest.TestCase):
    def open_results(self, page):
        search = build_global_search(page)
        search_field = search.content.controls[0]
        search_field.value = "10025735"
        with patch.object(
            ApiClient,
            "list_deportistas_page",
            return_value={
                "items": [
                    {
                        "IDENTI_DEPORTISTA": "10025735",
                        "NOMBRE_DEPORTISTA": "Francisco Medina",
                    }
                ]
            },
        ):
            search_field.on_submit(None)
        return page.opened[-1]

    def result_buttons(self, dialog):
        result_card = dialog.content.content.controls[0]
        result_row = result_card.content
        return result_row.controls[2], result_row.controls[3]

    def test_valorar_closes_dialog_before_deferred_navigation(self):
        page = FakePage()
        dialog = self.open_results(page)
        valorar_button, _ = self.result_buttons(dialog)

        with patch("src.frontend.navigation.show_valoracion") as navigate:
            valorar_button.on_click(None)

            self.assertFalse(dialog.open)
            self.assertEqual(page.closed, [dialog])
            navigate.assert_not_called()

            page.thread_callbacks.pop(0)()

        navigate.assert_called_once_with(page, "10025735")

    def test_historial_closes_dialog_before_deferred_navigation(self):
        page = FakePage()
        dialog = self.open_results(page)
        _, historial_button = self.result_buttons(dialog)

        with patch("src.frontend.navigation.show_historial") as navigate:
            historial_button.on_click(None)

            self.assertFalse(dialog.open)
            self.assertEqual(page.closed, [dialog])
            navigate.assert_not_called()

            page.thread_callbacks.pop(0)()

        navigate.assert_called_once_with(page, "10025735")


if __name__ == "__main__":
    unittest.main()
