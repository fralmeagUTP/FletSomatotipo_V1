import unittest

from app_config import handle_api_error, show_snack


class FakeSession:
    def __init__(self):
        self.values = {
            "access_token": "token",
            "login_user": "tester",
            "username": "Usuario",
            "user_id": "7",
        }

    def clear(self):
        self.values.clear()


class FakePage:
    def __init__(self):
        self.updated = 0
        self.snack_bar = None
        self.session = FakeSession()

    def update(self):
        self.updated += 1


class AppConfigTests(unittest.TestCase):
    def test_show_snack_opens_message_and_updates_page(self):
        page = FakePage()

        show_snack(page, "Mensaje")

        self.assertTrue(page.snack_bar.open)
        self.assertEqual(page.snack_bar.content.value, "Mensaje")
        self.assertEqual(page.updated, 1)

    def test_unauthorized_response_clears_all_session_values(self):
        page = FakePage()
        response = type("Response", (), {"status_code": 401})()

        handled = handle_api_error(page, response)

        self.assertTrue(handled)
        self.assertEqual(page.session.values, {})
        self.assertEqual(page.snack_bar.content.value, "Sesion expirada. Inicia sesion nuevamente.")


if __name__ == "__main__":
    unittest.main()
