import flet as ft

from src.frontend import theme
from src.frontend.assets import INSTITUTIONAL_LOGOS, LOGO_SOMATOCARTA, asset_src
from src.frontend.components import content_card, is_mobile, responsive_padding


def AcercaView(page: ft.Page):
    logos = ft.Row(
        [ft.Image(src=asset_src(page, logo), height=36, fit=ft.ImageFit.CONTAIN) for logo in INSTITUTIONAL_LOGOS],
        spacing=14,
        wrap=True,
    )

    def bullet(text):
        return ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=theme.PRIMARY_COLOR, size=18),
                ft.Text(text, size=13, color=theme.TEXT_COLOR, expand=True),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    if is_mobile(page):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=36),
                    ft.Image(src=asset_src(page, LOGO_SOMATOCARTA), width=112, height=112, fit=ft.ImageFit.CONTAIN),
                    ft.Text("Somatocarta", size=32, weight=ft.FontWeight.BOLD, color=theme.INK_COLOR, text_align=ft.TextAlign.CENTER),
                    ft.Text("Aplicacion de somatotipo", size=14, color=theme.MUTED_TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        content=ft.Text("Version v1.2.11", size=11, color=theme.PRIMARY_BLUE),
                        bgcolor=theme.INFO_BACKGROUND,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    ),
                    ft.Container(height=28),
                    ft.Text(
                        "Herramienta desarrollada para la evaluacion y analisis de la composicion corporal y somatotipo en deportistas.",
                        size=15,
                        color=theme.INK_COLOR,
                        text_align=ft.TextAlign.LEFT,
                    ),
                    ft.Container(height=12),
                    ft.Text("Desarrollado por:", size=11, color=theme.MUTED_TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                    logos,
                    ft.Container(expand=True),
                    ft.Text("(c) 2026 Todos los derechos reservados", size=11, color=theme.MUTED_TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(left=52, right=52, top=12, bottom=26),
            bgcolor=ft.Colors.WHITE,
            expand=True,
        )

    return ft.Container(
        content=ft.Column(
            [
                content_card(
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                ft.Image(src=asset_src(page, LOGO_SOMATOCARTA), width=120, height=120, fit=ft.ImageFit.CONTAIN),
                                col={"xs": 12, "md": 3},
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Text("Somatocarta", size=28, weight=ft.FontWeight.BOLD, color=theme.PRIMARY_COLOR),
                                        ft.Text(
                                            "Aplicación para registrar, analizar y consultar valoraciones antropométricas y somatotipo en población deportiva.",
                                            size=14,
                                            color=theme.TEXT_COLOR,
                                        ),
                                        ft.Text("Versión funcional del sistema de valoración corporal.", size=12, color=theme.SUBTITLE_COLOR),
                                    ],
                                    spacing=8,
                                ),
                                col={"xs": 12, "md": 9},
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
                content_card(
                    ft.Column(
                        [
                            ft.Text("Alcance del proyecto", size=18, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                            bullet("Gestiona deportistas, deportes, entidades y asignaciones deportivas."),
                            bullet("Permite crear y editar valoraciones corporales con múltiples tomas."),
                            bullet("Genera análisis de composición corporal, somatotipo y reportes PDF."),
                            bullet("Incluye análisis longitudinal para seguimiento temporal del deportista."),
                        ],
                        spacing=10,
                    ),
                    padding=20,
                ),
                content_card(
                    ft.Column(
                        [
                            ft.Text("Instituciones y soporte visual", size=18, weight=ft.FontWeight.BOLD, color=theme.HEADING_COLOR),
                            ft.Text("El sistema integra recursos gráficos y referencias de apoyo para facilitar la interpretación por parte del usuario final.", size=13, color=theme.SUBTITLE_COLOR),
                            logos,
                        ],
                        spacing=12,
                    ),
                    padding=20,
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=responsive_padding(page),
        bgcolor=theme.BACKGROUND_COLOR,
        expand=True,
    )
