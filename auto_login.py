import sys
import time
sys.path.insert(0, r'C:\Users\fralm\Desktop\Opencode_SomatoCarta')

import flet as ft
import requests
from src.frontend.api_client import ApiClient
from src.frontend.navigation import show_dashboard, set_logout_callback
from src.frontend import theme
from views.dashboard import DashboardView

BASE = "http://127.0.0.1:8085"
USERNAME = "admin"
PASSWORD = "CDR2026"

def main(page: ft.Page):
    page.title = "Somatocarta - Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = theme.BACKGROUND_COLOR
    
    # Login automático
    print(f"Intentando login con {USERNAME}...")
    r = requests.post(f"{BASE}/auth/login", json={"username": USERNAME, "password": PASSWORD}, timeout=10)
    
    if r.status_code != 200:
        page.add(ft.Text(f"Error de login: {r.status_code}", color="red"))
        page.update()
        return
    
    data = r.json()
    print(f"Login exitoso: {data.get('username')}")
    
    # Guardar en sesión
    page.session.set("username", data["username"])
    page.session.set("login_user", data["login_user"])
    page.session.set("access_token", data["access_token"])
    page.session.set("user_id", str(data["user_id"]))
    
    # Configurar logout
    def handle_logout():
        page.session.clear()
        page.controls.clear()
        page.add(ft.Text("Sesión cerrada. Recarga la página."))
        page.update()
    
    set_logout_callback(handle_logout)
    
    # Mostrar dashboard
    show_dashboard(page, handle_logout)
    print("Dashboard mostrado")

if __name__ == "__main__":
    ft.app(target=main)
