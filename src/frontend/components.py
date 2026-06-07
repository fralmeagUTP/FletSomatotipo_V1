import flet as ft

from src.frontend import theme


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
