import flet as ft


if not hasattr(ft, "Colors") and hasattr(ft, "colors"):
    ft.Colors = ft.colors
if not hasattr(ft, "Icons") and hasattr(ft, "icons"):
    ft.Icons = ft.icons
if not hasattr(ft, "ImageFit") and hasattr(ft, "BoxFit"):
    ft.ImageFit = ft.BoxFit
if not hasattr(ft, "FilePickerResultEvent") and hasattr(ft, "Event"):
    ft.FilePickerResultEvent = ft.Event

for module_name, type_name, helpers in (
    ("padding", "Padding", ("all", "only", "symmetric")),
    ("margin", "Margin", ("all", "only", "symmetric")),
    ("border", "Border", ("all", "only", "symmetric")),
    ("border_radius", "BorderRadius", ("all", "only")),
):
    helper_module = getattr(ft, module_name)
    helper_type = getattr(ft, type_name)
    for helper in helpers:
        if not hasattr(helper_module, helper):
            setattr(helper_module, helper, getattr(helper_type, helper))

for alignment_name in (
    "bottom_center",
    "bottom_left",
    "bottom_right",
    "center",
    "center_left",
    "center_right",
    "top_center",
    "top_left",
    "top_right",
):
    if not hasattr(ft.alignment, alignment_name):
        setattr(ft.alignment, alignment_name, getattr(ft.Alignment, alignment_name.upper()))

try:
    import flet_charts as flet_charts
except ImportError:
    flet_charts = None

if flet_charts is not None:
    for chart_control in (
        "ChartAxis",
        "ChartAxisLabel",
        "ChartCirclePoint",
        "ChartGridLines",
        "LineChart",
        "LineChartData",
        "LineChartDataPoint",
        "PieChart",
        "PieChartSection",
    ):
        if not hasattr(ft, chart_control):
            setattr(ft, chart_control, getattr(flet_charts, chart_control))


PRIMARY_COLOR = "#1f5fca"
PRIMARY_BLUE = "#2f66c9"
BACKGROUND_COLOR = "#f6f8fc"
MOBILE_BACKGROUND = "#f4f7fc"
CARD_BACKGROUND = ft.Colors.WHITE
TEXT_COLOR = "#243044"
HEADING_COLOR = "#172033"
INK_COLOR = "#202938"
APP_TITLE_COLOR = "#2c3e50"
SUBTITLE_COLOR = "#667085"
MUTED_TEXT_COLOR = "#6b7280"
INFO_BACKGROUND = "#edf4ff"
SURFACE_MUTED = "#f1f5fb"
SURFACE_BORDER = "#dbe5f2"
SUCCESS_COLOR = "#2e7d32"
SUCCESS_GREEN = "#34a853"
ERROR_COLOR = "#c62828"
WARNING_COLOR = "#f59e0b"

RADIUS_SMALL = 8
RADIUS_MEDIUM = 8
RADIUS_LARGE = 10
MOBILE_RADIUS = 12

SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24

TITLE_SIZE = 24
SECTION_TITLE_SIZE = 18
BODY_SIZE = 14
CAPTION_SIZE = 12


def card_shadow():
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=10,
        color="#140f2a4414",
        offset=ft.Offset(0, 4),
    )


def button_shape(radius=RADIUS_SMALL):
    return ft.RoundedRectangleBorder(radius=radius)
