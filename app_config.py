import os

from dotenv import load_dotenv


load_dotenv()


def _clean_base_url(value: str) -> str:
    return value.rstrip("/")


API_URL = _clean_base_url(os.getenv("API_URL", "http://127.0.0.1:8085"))
#API_URL = _clean_base_url(os.getenv("API_URL", "https://nyquist.app/somatocarta"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8085"))


def auth_headers(page):
    token = page.session.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def show_snack(page, message: str):
    import flet as ft

    page.snack_bar = ft.SnackBar(ft.Text(message))
    page.snack_bar.open = True
    if hasattr(page, "update"):
        page.update()


def api_error_message(response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Error del servidor"

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, list):
        messages = []
        for item in detail:
            location = item.get("loc", [])
            field = str(location[-1]) if location else "campo"
            message = item.get("msg", "valor invalido")
            messages.append(f"{field}: {message}")
        return "; ".join(messages)
    if detail:
        return str(detail)
    return "Error del servidor"


def handle_api_error(page, response, fallback: str = "No se pudo completar la operacion") -> bool:
    if response.status_code == 401:
        page.session.set("access_token", "")
        page.session.set("login_user", "")
        show_snack(page, "Sesion expirada. Inicia sesion nuevamente.")
        return True

    message = api_error_message(response) or fallback
    show_snack(page, message)
    return True
