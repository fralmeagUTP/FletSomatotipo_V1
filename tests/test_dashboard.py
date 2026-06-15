"""
Script de diagnóstico y auto-login para SomatoCarta
Muestra el dashboard directamente después del login
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
import requests
from src.frontend import theme
from src.frontend.assets import WINDOW_ICON, asset_path
from src.frontend.navigation import set_logout_callback

# Configuración
BASE_URL = "http://127.0.0.1:8085"
USERNAME = "admin"
PASSWORD = "CDR2026"

def check_backend_connection():
    """Verifica que el backend esté funcionando"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("✓ Backend conectado")
            return True
        else:
            print(f"✗ Backend respondió con status {r.status_code}")
            return False
    except Exception as e:
        print(f" No se puede conectar al backend: {e}")
        return False

def check_login():
    """Prueba el login y retorna los datos"""
    try:
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            print(f"✓ Login exitoso: {data.get('username')}")
            return data
        else:
            print(f"✗ Login falló: {r.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error en login: {e}")
        return None

def main(page: ft.Page):
    """Función principal de Flet"""
    page.title = "SomatoCarta - Dashboard"
    if hasattr(page, "window"):
        page.window.icon = asset_path(WINDOW_ICON)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Paso 1: Verificar backend
    print("\n=== DIAGNÓSTICO ===")
    if not check_backend_connection():
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=64),
                    ft.Text("Backend no disponible", size=20, color="red"),
                    ft.Text("Inicia el backend con: .\\start_backend.bat", size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center,
            )
        )
        page.update()
        return
    
    # Paso 2: Login
    user_data = check_login()
    if not user_data:
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOGIN, color="orange", size=64),
                    ft.Text("Login falló", size=20, color="orange"),
                    ft.Text(f"Usuario: {USERNAME}", size=14),
                    ft.Text(f"Contraseña: {PASSWORD}", size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center,
            )
        )
        page.update()
        return
    
    # Paso 3: Configurar sesión
    print("✓ Configurando sesión...")
    page.session.set("username", user_data["username"])
    page.session.set("login_user", user_data["login_user"])
    page.session.set("access_token", user_data["access_token"])
    page.session.set("user_id", str(user_data["user_id"]))
    
    # Paso 4: Importar y construir dashboard
    print("✓ Cargando dashboard...")
    try:
        from views.dashboard import DashboardView
        
        # Configurar logout
        def handle_logout():
            print("✓ Logout ejecutado")
            page.session.clear()
            page.controls.clear()
            page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=64),
                        ft.Text("Sesión cerrada", size=20),
                        ft.Text("Recarga la aplicación para iniciar sesión nuevamente", size=14),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
            page.update()
        
        set_logout_callback(handle_logout)
        
        # Construir dashboard
        print("✓ Construyendo UI del dashboard...")
        dashboard = DashboardView(page)
        
        # Limpiar y mostrar
        page.controls.clear()
        page.bgcolor = theme.BACKGROUND_COLOR
        page.add(dashboard)
        page.update()
        
        print("✓ Dashboard mostrado exitosamente")
        print("===================\n")
        
    except Exception as e:
        print(f"✗ Error al construir dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BUG_REPORT, color="red", size=64),
                    ft.Text("Error al cargar dashboard", size=20, color="red"),
                    ft.Text(str(e), size=12, color="grey"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center,
            )
        )
        page.update()

if __name__ == "__main__":
    print("Iniciando SomatoCarta con auto-login...")
    ft.app(target=main, assets_dir="assets")
