import sys
import os

def android_log(message: str):
    try:
        import ctypes

        liblog = ctypes.CDLL("liblog.so")
        liblog.__android_log_write(4, b"SomatocartaPy", str(message).encode("utf-8"))
    except Exception:
        pass


android_log("module import start")

# Ensure the current directory is in the path for module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

APP_VERSION = "v1.1.7"

def main(page):
    android_log("main(page) entered")
    global ft
    if "ft" not in globals():
        import flet as ft
        android_log("flet imported inside main")

    """
    Función principal de la aplicación Flet (Frontend).

    Configura la ventana principal y muestra la pantalla de inicio de sesión.

    Args:
        page (ft.Page): La página principal de Flet.
    """
    page.title = "Somatocarta"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.add(ft.Text("Iniciando Somatocarta...", size=18, color=ft.Colors.BLUE_700))
    page.update()
    android_log("startup text rendered")

    try:
        from app_config import API_URL
        from src.frontend import theme
        from src.frontend.api_client import ApiClient, ApiError
        from src.frontend.assets import (
            LOGO_CDR,
            LOGO_ISC,
            LOGO_NYQUIST,
            LOGO_SOMATOCARTA,
            LOGO_UTP,
            WINDOW_ICON,
            asset_path,
        )
        from src.frontend.navigation import show_dashboard
        android_log("app imports loaded")
    except Exception as ex:
        android_log(f"app import failed: {ex}")
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "No se pudo cargar la app",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(str(ex), size=13, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=20,
            )
        )
        page.update()
        return

    if hasattr(page, "window"):
        try:
            page.window.icon = asset_path(WINDOW_ICON)
        except Exception:
            pass
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE

    # Colors based on image
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    TEXT_COLOR = theme.TEXT_COLOR
    SUBTITLE_COLOR = theme.SUBTITLE_COLOR

    # --- UI Elements ---
    
    logo_icon = ft.Image(
        src=asset_path(LOGO_SOMATOCARTA),
        width=116,
        height=116,
        fit=ft.ImageFit.CONTAIN,
    )

    institutional_logos = ft.Row(
        [
            ft.Image(src=asset_path(LOGO_CDR), height=32, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_path(LOGO_ISC), height=32, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_path(LOGO_UTP), height=32, fit=ft.ImageFit.CONTAIN),
            ft.Image(src=asset_path(LOGO_NYQUIST), height=32, fit=ft.ImageFit.CONTAIN),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
    )


    username_field = ft.TextField(
        hint_text="Usuario",
        height=50,
        border_radius=8,
        border_color="#cccccc",
        focused_border_color=PRIMARY_COLOR,
        text_size=16,
        content_padding=ft.padding.only(left=15, right=15, top=5, bottom=5),
        bgcolor=ft.Colors.WHITE,
        color=TEXT_COLOR
    )
    
    password_field = ft.TextField(
        hint_text="Contraseña",
        password=True,
        height=50,
        border_radius=8,
        border_color="#cccccc",
        focused_border_color=PRIMARY_COLOR,
        can_reveal_password=False, 
        text_size=16,
        content_padding=ft.padding.only(left=15, right=15, top=5, bottom=5),
        bgcolor=ft.Colors.WHITE,
        color=TEXT_COLOR
    )

    error_text = ft.Text(color="red", visible=False, size=14)
    login_in_progress = False
    login_button_control = None

    def show_startup_error(ex: Exception):
        page.clean()
        page.bgcolor = ft.Colors.WHITE
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("No se pudo iniciar Somatocarta", size=22, weight=ft.FontWeight.BOLD, color=theme.ERROR_COLOR, text_align=ft.TextAlign.CENTER),
                        ft.Text(str(ex), size=14, color=theme.TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"API_URL: {API_URL}", size=12, color=theme.SUBTITLE_COLOR, text_align=ft.TextAlign.CENTER),
                        ft.Text("Cierra y vuelve a abrir la app.", size=12, color=theme.SUBTITLE_COLOR, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                width=520,
                padding=20,
            )
        )
        page.update()

    def build_login_ui():
        """Construye y retorna la UI de login"""
        nonlocal login_button_control
        login_button = ft.ElevatedButton(
            content=ft.Text("Iniciar sesión", size=16, weight="bold"),
            on_click=login_click,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=PRIMARY_COLOR,
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        login_button_control = login_button

        login_box = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=20),
                    ft.Container(
                        content=logo_icon,
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(bottom=10)
                    ),
                    ft.Text("Somatocarta", size=32, weight=ft.FontWeight.BOLD, color=theme.APP_TITLE_COLOR, text_align=ft.TextAlign.CENTER),
                    ft.Text("Aplicación de somatotipo", size=18, color=SUBTITLE_COLOR, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Versión: {APP_VERSION}", size=12, color="grey", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20), 
                    username_field,
                    ft.Container(height=5),
                    password_field,
                    ft.Container(height=5),
                    error_text,
                    ft.Container(height=15),
                    ft.Container(
                        content=login_button,
                        width=float("inf"),
                    ),
                    ft.Container(height=6),
                    institutional_logos,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            col={"xs": 12, "sm": 8, "md": 6, "lg": 4},
            bgcolor=ft.Colors.WHITE,
            padding=20,
        )

        return ft.ResponsiveRow(
            [login_box],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def show_login():
        """Muestra la pantalla de login"""
        nonlocal login_in_progress
        login_in_progress = False
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.bgcolor = ft.Colors.WHITE
        page.add(build_login_ui())
        page.update()

    def handle_logout():
        """Cierra la sesión y vuelve al login"""
        page.session.clear()
        username_field.value = ""
        password_field.value = ""
        error_text.value = ""
        error_text.visible = False
        show_login()

    def login_click(e):
        nonlocal login_in_progress
        if login_in_progress:
            return
        login_in_progress = True
        if login_button_control is not None:
            login_button_control.disabled = True
        error_text.value = ""
        error_text.visible = False
        page.update()
        login_success = False
        
        try:
            try:
                from views.dashboard import DashboardView
            except ImportError as ie:
                import os
                cwd = os.getcwd()
                files = sorted(os.listdir('.'))
                has_views = "views" in files
                flattened_views = [f for f in files if f.startswith("views") and "\\" in f]
                has_views_init = False
                if has_views:
                    try:
                        has_views_init = "__init__.py" in os.listdir('views')
                    except:
                        pass
                has_git = ".git" in files or any(f.startswith(".git") for f in files)
                error_msg = "INTENTANDO CORREGIR ARCHIVOS...\n"
                error_msg += f"Archivos Flattened Encontrados: {len(flattened_views)}\n"
                error_msg += "Por favor reinicia la app si ves esto.\n"
                error_msg += "Si el error persiste, la auto-reparación falló.\n\n"
                error_msg += f"VIEWS DIR: {has_views}\n"
                error_msg += f"GIT PRESENT: {has_git}\n"
                error_msg += f"CWD: {cwd}\n"
                error_msg += f"Error: {ie}\n"
                error_msg += f"Files (first 20): {files[:20]}" 
                error_text.value = error_msg
                error_text.visible = True
                page.update()
                return

            data = ApiClient(page).login(username_field.value, password_field.value)
            if data:
                page.session.set("username", data["username"])
                page.session.set("login_user", data["login_user"])
                page.session.set("access_token", data["access_token"])
                page.session.set("user_id", str(data["user_id"]))
                
                page.bgcolor = theme.BACKGROUND_COLOR
                show_dashboard(page, handle_logout)
                login_success = True
        except ApiError as error:
            error_text.value = str(error) or "Credenciales incorrectas"
            error_text.visible = True
        except Exception as ex:
            error_text.value = f"Error inesperado: {str(ex)}"
            error_text.visible = True
        finally:
            if not login_success:
                login_in_progress = False
                if login_button_control is not None:
                    login_button_control.disabled = False
        
        page.update()

    # Initial login screen
    try:
        page.add(build_login_ui())
        android_log("login rendered")
    except Exception as ex:
        android_log(f"login render failed: {ex}")
        show_startup_error(ex)

if __name__ == "__main__":
    import flet as ft
    android_log("flet imported before app")
    android_log("ft.app starting")
    ft.app(target=main, assets_dir="assets")

