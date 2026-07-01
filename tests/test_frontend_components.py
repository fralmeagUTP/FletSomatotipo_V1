import unittest
from unittest.mock import patch

from types import SimpleNamespace

import flet as ft

from src.frontend.app_shell import build_app_shell
from src.frontend.components import (
    content_card,
    horizontal_scroll,
    info_banner,
    is_android_app,
    is_mobile,
    mobile_search_field,
    mobile_screen,
    mobile_top_bar,
    page_header,
    responsive_dialog_size,
    responsive_padding,
    section_title,
    set_busy,
    uses_mobile_app_layout,
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

    def test_mobile_search_field_uses_standard_style_and_internal_action(self):
        queries = []
        field = mobile_search_field("Buscar deportista...", on_search=queries.append)

        self.assertEqual(field.height, 50)
        self.assertEqual(field.text_size, 14)
        self.assertEqual(field.border_radius, theme.MOBILE_RADIUS)
        self.assertEqual(field.focused_border_color, theme.PRIMARY_BLUE)
        self.assertIsInstance(field.suffix, ft.IconButton)

        field.value = "10025735"
        field.suffix.on_click(SimpleNamespace())
        field.on_submit(SimpleNamespace(control=field))

        self.assertEqual(queries, ["10025735", "10025735"])

    def test_page_header_without_back_button_has_only_title(self):
        header = page_header("Dashboard")

        self.assertEqual(len(header.controls), 1)
        self.assertEqual(header.controls[0].value, "Dashboard")

    def test_mobile_top_bar_logout_button_runs_callback(self):
        calls = []
        header = mobile_top_bar("Dashboard", on_menu=lambda _: None, on_trailing=lambda _: calls.append("logout"))
        logout_button = header.content.content.controls[-1]

        self.assertFalse(logout_button.disabled)
        logout_button.on_click(None)
        self.assertEqual(calls, ["logout"])

    def test_unknown_width_defaults_to_mobile_layout(self):
        page = SimpleNamespace(width=None)

        self.assertTrue(is_mobile(page))

    def test_force_mobile_env_overrides_desktop_width(self):
        page = SimpleNamespace(width=1280)

        with patch.dict("os.environ", {"SOMATOCARTA_FORCE_MOBILE": "1"}):
            self.assertTrue(is_mobile(page))

    def test_narrow_web_page_keeps_web_layout(self):
        page = SimpleNamespace(width=390, web=True)

        self.assertFalse(is_mobile(page))
        self.assertFalse(uses_mobile_app_layout(page, 900))

    def test_narrow_native_page_uses_mobile_app_layout(self):
        page = SimpleNamespace(width=390, web=False)

        self.assertTrue(is_mobile(page))
        self.assertTrue(uses_mobile_app_layout(page, 900))

    def test_android_tablet_keeps_mobile_app_layout_at_desktop_width(self):
        page = SimpleNamespace(width=1280, web=False, platform="android")

        self.assertTrue(is_android_app(page))
        self.assertTrue(is_mobile(page))
        self.assertTrue(uses_mobile_app_layout(page, 900))

    def test_android_environment_keeps_mobile_layout_without_platform_metadata(self):
        page = SimpleNamespace(width=1280, web=False, platform=None)

        with patch.dict("os.environ", {"ANDROID_ROOT": "/system"}):
            self.assertTrue(is_android_app(page))
            self.assertTrue(is_mobile(page))

    def test_wide_native_desktop_still_uses_desktop_layout(self):
        page = SimpleNamespace(width=1280, web=False, platform="windows")

        self.assertFalse(is_android_app(page))
        self.assertFalse(is_mobile(page))

    def test_web_runtime_wins_over_android_environment(self):
        page = SimpleNamespace(width=390, web=True, platform="android")

        with patch.dict("os.environ", {"ANDROID_ROOT": "/system", "APP_RUNTIME": "web"}):
            self.assertFalse(is_android_app(page))
            self.assertFalse(is_mobile(page))

    def test_mobile_top_bar_respects_android_status_bar_safe_area(self):
        bar = mobile_top_bar("Dashboard", on_menu=lambda _: None, on_trailing=lambda _: None)

        self.assertIsInstance(bar, ft.SafeArea)
        self.assertTrue(bar.avoid_intrusions_top)
        self.assertFalse(bar.avoid_intrusions_bottom)
        self.assertEqual(bar.content.height, 64)

    def test_bottom_navigation_respects_android_navigation_safe_area(self):
        page = SimpleNamespace(width=390, session={}, overlay=[], update=lambda: None)
        shell = build_app_shell(page, ft.Text("Contenido"), title="Dashboard", show_search=False)
        bottom_navigation = shell.content.controls[1].controls[4]

        self.assertIsInstance(bottom_navigation, ft.SafeArea)
        self.assertFalse(bottom_navigation.avoid_intrusions_top)
        self.assertTrue(bottom_navigation.avoid_intrusions_bottom)
        self.assertTrue(bottom_navigation.maintain_bottom_view_padding)
        self.assertEqual(bottom_navigation.content.height, 72)

    def test_mobile_screen_bottom_action_respects_android_navigation_safe_area(self):
        screen = mobile_screen(ft.Text("Contenido"), bottom_action=ft.Text("Guardar"))
        bottom_action = screen.content.controls[-1]

        self.assertIsInstance(bottom_action, ft.SafeArea)
        self.assertFalse(bottom_action.avoid_intrusions_top)
        self.assertTrue(bottom_action.avoid_intrusions_bottom)
        self.assertTrue(bottom_action.maintain_bottom_view_padding)

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
        self.assertEqual(responsive_padding(SimpleNamespace(width=1280)), 24)

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

    def test_app_shell_uses_mobile_layout_when_width_is_unknown(self):
        page = SimpleNamespace(width=None, session={}, overlay=[], update=lambda: None)

        shell = build_app_shell(page, ft.Text("Contenido"), title="Dashboard", show_search=False)
        sidebar, body = shell.content.controls
        top_bar = body.controls[0]
        mobile_header = body.controls[1]
        bottom_navigation = body.controls[4]

        self.assertFalse(sidebar.visible)
        self.assertFalse(top_bar.visible)
        self.assertTrue(mobile_header.visible)
        self.assertTrue(bottom_navigation.visible)

    def test_app_shell_keeps_web_shell_on_narrow_browser(self):
        page = SimpleNamespace(width=390, web=True, session={}, overlay=[], update=lambda: None)

        shell = build_app_shell(page, ft.Text("Contenido"), title="Dashboard", show_search=False)
        sidebar, body = shell.content.controls
        top_bar = body.controls[0]
        mobile_header = body.controls[1]
        bottom_navigation = body.controls[4]

        self.assertTrue(sidebar.visible)
        self.assertFalse(top_bar.visible)
        self.assertFalse(mobile_header.visible)
        self.assertFalse(bottom_navigation.visible)


if __name__ == "__main__":
    unittest.main()
