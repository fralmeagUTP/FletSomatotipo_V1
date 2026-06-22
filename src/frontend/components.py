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
    return ft.Row([content], scroll=ft.ScrollMode.AUTO, width=float("inf"))


def page_header(title: str, on_back=None, color: str = theme.TEXT_COLOR):
    controls = []
    if on_back:
        controls.append(ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back, icon_color=color))
    controls.append(ft.Text(title, size=theme.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=color, expand=True))
    return ft.Row(controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def info_banner(text: str, icon=ft.Icons.INFO_OUTLINE):
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, color=theme.PRIMARY_COLOR, size=30),
                ft.Container(width=15),
                ft.Text(text, size=16, color=theme.TEXT_COLOR, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=theme.INFO_BACKGROUND,
        padding=20,
        border_radius=theme.RADIUS_MEDIUM,
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
        border_radius=theme.RADIUS_SMALL,
    )


def section_title(text: str):
    return ft.Text(text, size=theme.SECTION_TITLE_SIZE, weight="bold", color=theme.PRIMARY_COLOR)


def content_card(content, padding=10, radius=theme.RADIUS_MEDIUM):
    return ft.Container(
        bgcolor=theme.CARD_BACKGROUND,
        border_radius=radius,
        padding=padding,
        shadow=theme.card_shadow(),
        content=content,
    )


def screen_container(page, content, desktop=40, tablet=24, mobile=12):
    return ft.Container(
        content=content,
        padding=responsive_padding(page, desktop=desktop, tablet=tablet, mobile=mobile),
        bgcolor=theme.BACKGROUND_COLOR,
        expand=True,
    )


def primary_button(text: str, icon=None, on_click=None):
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        bgcolor=theme.PRIMARY_COLOR,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=theme.button_shape()),
    )


def secondary_button(text: str, icon=None, on_click=None, visible=True):
    return ft.OutlinedButton(
        text,
        icon=icon,
        on_click=on_click,
        visible=visible,
        style=ft.ButtonStyle(shape=theme.button_shape()),
    )


ACTION_ICON_SIZE = 22
ACTION_BUTTON_SIZE = 40


def danger_icon_button(icon=ft.Icons.DELETE, on_click=None, tooltip="Eliminar"):
    return ft.IconButton(
        icon,
        icon_color=theme.ERROR_COLOR,
        icon_size=ACTION_ICON_SIZE,
        tooltip=tooltip,
        on_click=on_click,
        width=ACTION_BUTTON_SIZE,
        height=ACTION_BUTTON_SIZE,
    )


def edit_icon_button(on_click=None, tooltip="Editar"):
    return ft.IconButton(
        ft.Icons.EDIT,
        icon_color=theme.PRIMARY_COLOR,
        icon_size=ACTION_ICON_SIZE,
        tooltip=tooltip,
        on_click=on_click,
        width=ACTION_BUTTON_SIZE,
        height=ACTION_BUTTON_SIZE,
    )


def crud_row_card(content, actions=None):
    row_controls = [
        ft.Container(content=content, col={"xs": 12, "sm": 8, "md": 9}),
    ]
    if actions:
        row_controls.append(
            ft.Container(
                ft.Row(actions, spacing=4),
                col={"xs": 12, "sm": 4, "md": 3},
                alignment=ft.alignment.center_right,
            )
        )
    return ft.Container(
        content=ft.ResponsiveRow(
            row_controls,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=theme.CARD_BACKGROUND,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=theme.RADIUS_MEDIUM,
        padding=12,
    )


def confirm_delete_dialog(title: str, message: str, on_confirm, page=None):
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(event):
        target_page = page or getattr(event, "page", None)
        if target_page is not None:
            target_page.close(dialog)

    def confirm(event):
        on_confirm(event)
        close_dialog(event)

    dialog.actions = [
        ft.TextButton("Cancelar", on_click=close_dialog),
        ft.TextButton("Eliminar", on_click=confirm, style=ft.ButtonStyle(color=theme.ERROR_COLOR)),
    ]
    return dialog


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
