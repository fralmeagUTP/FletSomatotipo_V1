import unittest

from src.frontend.components import content_card, info_banner, page_header, section_title
from src.frontend import theme


class ComponentsTests(unittest.TestCase):
    def test_page_header_adds_back_button_when_callback_exists(self):
        header = page_header("Deportistas", on_back=lambda event: None)

        self.assertEqual(len(header.controls), 2)
        self.assertEqual(header.controls[1].value, "Deportistas")

    def test_page_header_without_back_button_has_only_title(self):
        header = page_header("Dashboard")

        self.assertEqual(len(header.controls), 1)
        self.assertEqual(header.controls[0].value, "Dashboard")

    def test_info_banner_uses_theme_background(self):
        banner = info_banner("Mensaje")

        self.assertEqual(banner.bgcolor, theme.INFO_BACKGROUND)
        self.assertEqual(banner.width, float("inf"))

    def test_section_title_uses_primary_color(self):
        title = section_title("Datos Básicos")

        self.assertEqual(title.color, theme.PRIMARY_COLOR)

    def test_content_card_wraps_content(self):
        content = object()
        card = content_card(content)

        self.assertIs(card.content, content)
        self.assertEqual(card.bgcolor, theme.CARD_BACKGROUND)


if __name__ == "__main__":
    unittest.main()
