import os

import flet as ft

from src.frontend import theme


def page_width(page, default=1024):
    if os.getenv("SOMATOCARTA_FORCE_MOBILE", "").strip().lower() in {"1", "true", "yes"}:
        return 390
    width = getattr(page, "width", None)
    return width or default


def is_compact(page):
    return page_width(page) < 600


def uses_mobile_app_layout(page, breakpoint=700):
    if os.getenv("SOMATOCARTA_FORCE_MOBILE", "").strip().lower() in {"1", "true", "yes"}:
        return True
    if bool(getattr(page, "web", False)):
        return False
    return page_width(page, default=390) < breakpoint


def is_mobile(page):
    return uses_mobile_app_layout(page)


def responsive_padding(page, desktop=24, tablet=24, mobile=12):
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
        controls.append(ft.IconButton(ft.Icons.ARROW_BACK, on_click=on_back, icon_color=color, icon_size=20))
    controls.append(ft.Text(title, size=theme.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=color, expand=True))
    return ft.Row(controls, vertical_alignment=ft.CrossAxisAlignment.CENTER, height=38)


def mobile_top_bar(title: str, on_back=None, on_menu=None, trailing_icon=ft.Icons.LOGOUT, on_trailing=None):
    leading = ft.IconButton(
        ft.Icons.ARROW_BACK if on_back else ft.Icons.MENU,
        icon_color=theme.INK_COLOR,
        icon_size=22,
        on_click=on_back or on_menu,
    )
    return ft.SafeArea(
        content=ft.Container(
            content=ft.Row(
                [
                    leading,
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme.INK_COLOR, expand=True),
                    ft.IconButton(
                        trailing_icon,
                        icon_color=theme.INK_COLOR,
                        icon_size=18,
                        tooltip="Cerrar sesión",
                        on_click=on_trailing,
                        disabled=on_trailing is None,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=64,
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.only(left=4, right=8),
            border=ft.border.only(bottom=ft.BorderSide(1, theme.SURFACE_BORDER)),
        ),
        avoid_intrusions_top=True,
        avoid_intrusions_left=True,
        avoid_intrusions_right=True,
        avoid_intrusions_bottom=False,
        expand=False,
    )


def mobile_search_field(hint: str, on_submit=None, on_search=None, value=None):
    field = ft.TextField(
        hint_text=hint,
        value=value,
        border_radius=theme.MOBILE_RADIUS,
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY_BLUE,
        bgcolor=ft.Colors.WHITE,
        height=50,
        text_size=14,
        dense=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
    )
    if on_search is not None:
        field.suffix = ft.IconButton(
            ft.Icons.SEARCH,
            icon_color=theme.PRIMARY_BLUE,
            icon_size=20,
            tooltip="Buscar",
            on_click=lambda _: on_search(field.value or ""),
        )
        field.on_submit = lambda event: on_search(event.control.value or "")
    else:
        field.suffix_icon = ft.Icons.SEARCH
        field.on_submit = on_submit
    return field


def mobile_primary_button(text: str, icon=ft.Icons.ADD, on_click=None, color=None):
    return ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(icon, color=ft.Colors.WHITE, size=18),
                ft.Text(text, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        on_click=on_click,
        height=44,
        bgcolor=color or theme.PRIMARY_BLUE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), elevation=0),
    )


def mobile_avatar(label: str, color="#dbeafe"):
    initials = "".join([part[:1] for part in (label or "-").split()[:2]]).upper() or "-"
    return ft.Container(
        content=ft.Text(initials, size=11, color=theme.INK_COLOR),
        width=34,
        height=34,
        bgcolor=color,
        border_radius=17,
        alignment=ft.alignment.center,
    )


def mobile_list_card(title: str, subtitle: str, avatar_text="", avatar_color="#dbeafe", on_click=None, trailing=True):
    controls = [
        mobile_avatar(avatar_text or title, avatar_color),
        ft.Column(
            [
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=theme.INK_COLOR, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(subtitle, size=11, color=theme.MUTED_TEXT_COLOR, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            ],
            spacing=2,
            expand=True,
        ),
    ]
    if trailing:
        controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=theme.MUTED_TEXT_COLOR))
    return ft.Container(
        content=ft.Row(controls, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        border_radius=theme.MOBILE_RADIUS,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        ink=on_click is not None,
        on_click=on_click,
    )


def mobile_screen(content, bottom_action=None):
    controls = [
        ft.Container(
            content=content,
            padding=ft.padding.only(left=22, right=22, top=18, bottom=18),
            expand=True,
        )
    ]
    if bottom_action is not None:
        controls.append(
            ft.SafeArea(
                content=ft.Container(
                    content=bottom_action,
                    padding=ft.padding.only(left=22, right=22, bottom=22, top=8),
                ),
                avoid_intrusions_top=False,
                avoid_intrusions_left=True,
                avoid_intrusions_right=True,
                avoid_intrusions_bottom=True,
                maintain_bottom_view_padding=True,
            )
        )
    return ft.Container(
        content=ft.Column(controls, spacing=0, expand=True),
        bgcolor=theme.MOBILE_BACKGROUND,
        expand=True,
    )


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
        border=ft.border.all(1, theme.SURFACE_BORDER),
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
        height=38,
        bgcolor=theme.PRIMARY_COLOR,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=theme.button_shape(), elevation=0),
    )


def secondary_button(text: str, icon=None, on_click=None, visible=True):
    return ft.OutlinedButton(
        text,
        icon=icon,
        on_click=on_click,
        visible=visible,
        height=38,
        style=ft.ButtonStyle(shape=theme.button_shape()),
    )


ACTION_ICON_SIZE = 22
ACTION_BUTTON_SIZE = 40


def pdf_action_button(on_click=None, *, mobile=False, disabled=False):
    return ft.Button(
        "Compartir PDF" if mobile else "Descargar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        tooltip="Compartir PDF" if mobile else "Descargar PDF",
        disabled=disabled,
        on_click=on_click,
        style=ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
        ),
    )


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
