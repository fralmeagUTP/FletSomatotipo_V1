import flet as ft

from src.frontend import theme


def page_width(page, default=1024):
    width = getattr(page, "width", None)
    return width or default


def is_compact(page):
    return page_width(page) < 600


def responsive_padding(page, desktop=40, tablet=24, mobile=12):
    width = page_width(page)
    if width < 600:
        return mobile
    if width < 1024:
        return tablet
    return desktop


def responsive_dialog_size(page, max_width=650, max_height=600):
    width = page_width(page)
    height = getattr(page, "height", None) or 760
    return {
        "width": min(max_width, max(width - 32, 320)),
        "height": min(max_height, max(height - 120, 420)),
    }


def horizontal_scroll(content):
    return ft.Row([content], scroll=ft.ScrollMode.AUTO)


def page_header(title: str, on_back=None, color: str = theme.TEXT_COLOR):
    controls = []
    if on_back:
        controls.append(ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back, icon_color=color))
    controls.append(ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=color))
    return ft.Row(controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def info_banner(text: str, icon=ft.Icons.INFO_OUTLINE):
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, color=theme.PRIMARY_COLOR, size=30),
                ft.Container(width=15),
                ft.Text(text, size=16, color=theme.TEXT_COLOR),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=theme.INFO_BACKGROUND,
        padding=20,
        border_radius=10,
        width=float("inf"),
    )


def inline_status(text_control, icon=ft.Icons.INFO_OUTLINE):
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, color=theme.PRIMARY_COLOR),
                text_control,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=theme.INFO_BACKGROUND,
        padding=12,
        border_radius=8,
    )


def section_title(text: str):
    return ft.Text(text, size=18, weight="bold", color=theme.PRIMARY_COLOR)


def content_card(content):
    return ft.Container(
        bgcolor=theme.CARD_BACKGROUND,
        border_radius=10,
        padding=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLUE_GREY_50),
        content=content,
    )


def empty_state(text: str, icon=ft.Icons.INFO_OUTLINE):
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=32, color=theme.SUBTITLE_COLOR),
                ft.Text(text, color=theme.SUBTITLE_COLOR, text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        padding=20,
    )


def set_busy(page, controls, is_busy: bool, status_text=None, busy_message: str | None = None):
    for control in controls:
        control.disabled = is_busy
    if status_text is not None and busy_message is not None:
        status_text.value = busy_message
    page.update()
