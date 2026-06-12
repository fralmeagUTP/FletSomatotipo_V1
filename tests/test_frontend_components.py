import unittest

from types import SimpleNamespace

import flet as ft

from src.frontend.components import (
    content_card,
    horizontal_scroll,
    info_banner,
    page_header,
    responsive_dialog_size,
    responsive_padding,
    section_title,
    set_busy,
)
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

    def test_set_busy_disables_controls_and_updates_status(self):
        page = SimpleNamespace(updated=False)
        page.update = lambda: setattr(page, "updated", True)
        control = SimpleNamespace(disabled=False)
        status = SimpleNamespace(value="")

        set_busy(page, [control], True, status, "Cargando...")

        self.assertTrue(control.disabled)
        self.assertEqual(status.value, "Cargando...")
        self.assertTrue(page.updated)

    def test_responsive_padding_uses_mobile_tablet_and_desktop_values(self):
        self.assertEqual(responsive_padding(SimpleNamespace(width=390)), 12)
        self.assertEqual(responsive_padding(SimpleNamespace(width=800)), 24)
        self.assertEqual(responsive_padding(SimpleNamespace(width=1280)), 40)

    def test_responsive_dialog_size_never_exceeds_viewport(self):
        size = responsive_dialog_size(SimpleNamespace(width=390, height=700))

        self.assertEqual(size["width"], 358)
        self.assertEqual(size["height"], 580)

    def test_horizontal_scroll_wraps_wide_content(self):
        content = ft.Text("contenido")
        row = horizontal_scroll(content)

        self.assertEqual(row.controls[0], content)
        self.assertEqual(row.scroll, ft.ScrollMode.AUTO)


if __name__ == "__main__":
    unittest.main()
