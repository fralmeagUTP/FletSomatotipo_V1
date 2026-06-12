import unittest

from src.frontend.navigation import show_view


class FakePage:
    def __init__(self):
        self.controls = [{"old": "content"}]
        self.session = {}

    def clean(self):
        self.controls.clear()

    def add(self, control):
        self.controls.append(control)


class NavigationTests(unittest.TestCase):
    def test_show_view_replaces_current_page_content(self):
        page = FakePage()

        show_view(page, lambda current_page: {"page": current_page})

        self.assertEqual(len(page.controls), 1)
        self.assertEqual(page.controls, [{"page": page}])


if __name__ == "__main__":
    unittest.main()
