import flet as ft


if not hasattr(ft, "Colors") and hasattr(ft, "colors"):
    ft.Colors = ft.colors
if not hasattr(ft, "Icons") and hasattr(ft, "icons"):
    ft.Icons = ft.icons


PRIMARY_COLOR = "#2e5cb8"
BACKGROUND_COLOR = "#f5f7fb"
CARD_BACKGROUND = ft.Colors.WHITE
TEXT_COLOR = "#333333"
HEADING_COLOR = "#1a1a1a"
APP_TITLE_COLOR = "#2c3e50"
SUBTITLE_COLOR = "#666666"
INFO_BACKGROUND = "#e8f0fe"
SURFACE_MUTED = "#f0f2f5"
SURFACE_BORDER = "#e3e8f0"
SUCCESS_COLOR = "#2e7d32"
ERROR_COLOR = "#c62828"
WARNING_COLOR = "#f59e0b"

RADIUS_SMALL = 8
RADIUS_MEDIUM = 10
RADIUS_LARGE = 12

SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24

TITLE_SIZE = 28
SECTION_TITLE_SIZE = 18
BODY_SIZE = 14
CAPTION_SIZE = 12


def card_shadow():
    return ft.BoxShadow(
        spread_radius=1,
        blur_radius=5,
        color=ft.Colors.BLUE_GREY_50,
        offset=ft.Offset(0, 5),
    )


def button_shape(radius=RADIUS_SMALL):
    return ft.RoundedRectangleBorder(radius=radius)
