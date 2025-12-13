import flet as ft
import requests
from views.dashboard import DashboardView

API_URL = "http://127.0.0.1:8085"
APP_VERSION = "v1.1.0"

def main(page: ft.Page):
    """
    Función principal de la aplicación Flet (Frontend).

    Configura la ventana principal y muestra la pantalla de inicio de sesión.

    Args:
        page (ft.Page): La página principal de Flet.
    """
    page.title = "Somatocarta"
    # page.window_width = 400
    # page.window_height = 700
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE

    # Colors based on image
    PRIMARY_COLOR = "#2e5cb8" # Approximation of the blue in the image
    TEXT_COLOR = "#333333"
    SUBTITLE_COLOR = "#666666"

    # --- UI Elements ---
    
    # Logo / Icon area
    # Since we don't have the exact hexagon image, using a placeholder icon stack
    logo_icon = ft.Stack(
        [
            ft.Icon(ft.Icons.HEXAGON_OUTLINED, size=100, color=PRIMARY_COLOR),
            ft.Icon(ft.Icons.ACCESSIBILITY_NEW, size=50, color=PRIMARY_COLOR),
        ],
        alignment=ft.alignment.center
    )


    username_field = ft.TextField(
        hint_text="Usuario",
        # width=320, removed for responsive
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
        # width=320,
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

    def login_click(e):
        error_text.value = ""
        error_text.visible = False
        page.update()
        
        try:
            response = requests.post(f"{API_URL}/auth/login", json={
                "username": username_field.value,
                "password": password_field.value
            })
            
            if response.status_code == 200:
                data = response.json()
                page.snack_bar = ft.SnackBar(ft.Text(f"Bienvenido {data['username']}!"))
                page.snack_bar.open = True
                
                # Store session user
                page.session.set("username", data["username"])
                
                page.clean()
                # page.add(ft.Text("Login Exitoso! Dashboard en construcción...", size=20, color=TEXT_COLOR))
                page.bgcolor = "#f5f7fb" # Match dashboard bg
                page.add(DashboardView(page))
            else:
                try:
                    detail = response.json().get("detail", "Credenciales incorrectas")
                except:
                    detail = "Error en el servidor"
                error_text.value = detail
                error_text.visible = True
        except Exception as ex:
            error_text.value = f"Error de conexión: {str(ex)}"
            error_text.visible = True
        
        page.update()

    login_button = ft.ElevatedButton(
        content=ft.Text("Iniciar sesión", size=16, weight="bold"),
        on_click=login_click,
        # width=320,
        height=50,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=PRIMARY_COLOR,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    # --- Layout ---
    # Responsive container for the login box
    login_box = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=20),
                # Icon
                ft.Container(
                    content=logo_icon,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10)
                ),
                # Title
                ft.Text("Somatocarta", size=32, weight=ft.FontWeight.BOLD, color="#2c3e50", text_align=ft.TextAlign.CENTER),
                # Subtitle
                ft.Text("Aplicación de somatotipo", size=18, color=SUBTITLE_COLOR, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Versión: {APP_VERSION}", size=12, color="grey", text_align=ft.TextAlign.CENTER),
                
                ft.Container(height=20), 
                
                # Inputs
                username_field,
                ft.Container(height=5),
                password_field,
                
                ft.Container(height=5),
                error_text,
                ft.Container(height=15),
                
                # Button
                ft.Container(
                    content=login_button,
                    width=float("inf"), # Button expands to full width of this column
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Centered content inside the box
            spacing=10
        ),
        col={"xs": 10, "sm": 8, "md": 6, "lg": 4}, # Responsive width
        bgcolor=ft.Colors.WHITE,
        # padding=20, # Optional: add padding if it was a card
    )

    page.add(
        ft.ResponsiveRow(
            [
                login_box
            ],
            alignment=ft.MainAxisAlignment.CENTER, # Center the column in the row
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
