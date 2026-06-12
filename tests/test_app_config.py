import unittest

from app_config import show_snack


class FakePage:
    def __init__(self):
        self.updated = 0
        self.snack_bar = None

    def update(self):
        self.updated += 1


class AppConfigTests(unittest.TestCase):
    def test_show_snack_opens_message_and_updates_page(self):
        page = FakePage()

        show_snack(page, "Mensaje")

        self.assertTrue(page.snack_bar.open)
        self.assertEqual(page.snack_bar.content.value, "Mensaje")
        self.assertEqual(page.updated, 1)


if __name__ == "__main__":
    unittest.main()
