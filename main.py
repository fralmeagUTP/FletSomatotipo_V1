import sys
import os
import shutil

# Ensure the current directory is in the path for module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_flattened_files():
    """
    Workaround for Flet build flattening directories into filenames on Android.
    e.g., 'views\dashboard.py' becomes a file named 'views\dashboard.py' instead of 'views/dashboard.py'.
    This function detects such files and moves them to their correct directories.
    """
    try:
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        fixed_count = 0
        
        for filename in files:
            if "\\" in filename:
                # This is a flattened file (e.g., "views\dashboard.py")
                # On Linux/Android, backslash is just a character
                parts = filename.split("\\")
                if len(parts) > 1:
                    # Create the directory structure
                    directory = os.path.join(current_dir, *parts[:-1])
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    
                    # Move/Rename the file
                    new_path = os.path.join(directory, parts[-1])
                    old_path = os.path.join(current_dir, filename)
                    
                    # Rename atomic
                    shutil.move(old_path, new_path)
                    fixed_count += 1
        return fixed_count
    except Exception as e:
        print(f"Error fixing files: {e}")
        return 0

# Run the fix immediately
fix_flattened_files()

import flet as ft
import requests
# from views.dashboard import DashboardView (Deferred import)

API_URL = "http://192.168.1.105:8085"
APP_VERSION = "v1.1.1"

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
            # Try to verify imports early to fail fast if module missing (Debug)
            try:
                from views.dashboard import DashboardView
            except ImportError as ie:
                # DEBUG: Show what is wrong
                import os
                cwd = os.getcwd()
                files = sorted(os.listdir('.'))
                
                # Check specifics
                has_views = "views" in files
                
                # Check for "flattened" file names (e.g. "views\dashboard.py")
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
                
                # Import here properly
                from views.dashboard import DashboardView
                page.add(DashboardView(page))
            else:
                try:
                    detail = response.json().get("detail", "Credenciales incorrectas")
                except:
                    detail = "Error en el servidor"
                error_text.value = detail
                error_text.visible = True
        except Exception as ex:
            import traceback
            error_text.value = f"Error: {str(ex)}\n{traceback.format_exc()}"
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
