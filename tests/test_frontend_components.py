import unittest

from types import SimpleNamespace

import flet as ft

from src.frontend.app_shell import build_app_shell
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
    def _collect_text_values(self, control):
        values = []
        value = getattr(control, "value", None)
        if isinstance(value, str):
            values.append(value)
        content = getattr(control, "content", None)
        if content is not None:
            values.extend(self._collect_text_values(content))
        for child in getattr(control, "controls", []) or []:
            values.extend(self._collect_text_values(child))
        return values

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
        self.assertEqual(row.width, float("inf"))

    def test_app_shell_switches_between_mobile_menu_and_sidebar_on_resize(self):
        page = SimpleNamespace(width=390, session={}, overlay=[], update_count=0)
        page.update = lambda: setattr(page, "update_count", page.update_count + 1)
        previous_resize_calls = []
        page.on_resized = lambda event: previous_resize_calls.append(event)

        shell = build_app_shell(page, ft.Text("Contenido"), title="Dashboard")
        sidebar, body = shell.content.controls
        mobile_menu = body.controls[0].content.controls[0]

        self.assertFalse(sidebar.visible)
        self.assertTrue(mobile_menu.visible)

        page.width = 1280
        resize_event = object()
        page.on_resized(resize_event)

        self.assertTrue(sidebar.visible)
        self.assertFalse(mobile_menu.visible)
        self.assertEqual(previous_resize_calls, [resize_event])
        self.assertEqual(page.update_count, 1)

    def test_app_shell_hides_text_header_when_no_search_or_actions(self):
        page = SimpleNamespace(width=1280, session={}, overlay=[], update=lambda: None)

        shell = build_app_shell(page, ft.Text("Contenido"), title="Dashboard", show_search=False)
        body = shell.content.controls[1]
        top_bar = body.controls[0]

        self.assertFalse(top_bar.visible)
        self.assertNotIn("Dashboard", self._collect_text_values(top_bar))
        self.assertNotIn("Panel operativo de Somatocarta", self._collect_text_values(top_bar))


if __name__ == "__main__":
    unittest.main()
