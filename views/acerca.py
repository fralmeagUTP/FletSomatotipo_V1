import flet as ft

from src.frontend import theme
from src.frontend.assets import LOGO_CDR, LOGO_ISC, LOGO_NYQUIST, LOGO_SOMATOCARTA, LOGO_UTP, asset_src
from src.frontend.components import content_card, responsive_padding


def AcercaView(page: ft.Page):
    logos = ft.Row(
        [
            ft.Image(src=asset_src(page, LOGO_CDR), height=36, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_src(page, LOGO_ISC), height=36, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_src(page, LOGO_UTP), height=36, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_src(page, LOGO_NYQUIST), height=36, fit=ft.ImageFit.CONTAIN),
        ],
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
