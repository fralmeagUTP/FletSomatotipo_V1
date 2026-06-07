import flet as ft


PRIMARY_COLOR = "#2e5cb8"
BACKGROUND_COLOR = "#f5f7fb"
CARD_BACKGROUND = ft.Colors.WHITE
TEXT_COLOR = "#333333"
HEADING_COLOR = "#1a1a1a"
APP_TITLE_COLOR = "#2c3e50"
SUBTITLE_COLOR = "#666666"
INFO_BACKGROUND = "#e8f0fe"
SURFACE_MUTED = "#f0f2f5"


def card_shadow():
    return ft.BoxShadow(
        spread_radius=1,
        blur_radius=5,
        color=ft.Colors.BLUE_GREY_50,
        offset=ft.Offset(0, 5),
    )
