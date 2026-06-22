import os

from dotenv import load_dotenv


load_dotenv()


def _clean_base_url(value: str) -> str:
    return value.rstrip("/")


API_URL = _clean_base_url(os.getenv("API_URL", "http://127.0.0.1:8085"))
#API_URL = _clean_base_url(os.getenv("API_URL", "https://nyquist.app/somatocarta"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8085"))
APP_RUNTIME = os.getenv("APP_RUNTIME", "native").strip().lower()
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8550"))


def is_web_runtime(page=None) -> bool:
    if page is not None and bool(getattr(page, "web", False)):
        return True
    return APP_RUNTIME == "web"


def session_store(page):
    session = page.session
    return getattr(session, "store", session)


def session_set(page, key, value):
    session_store(page).set(key, value)


def session_get(page, key):
    return session_store(page).get(key)


def session_clear(page):
    session_store(page).clear()


def auth_headers(page):
    token = session_get(page, "access_token")
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
        session_clear(page)
        show_snack(page, "Sesion expirada. Inicia sesion nuevamente.")
        return True

    message = api_error_message(response) or fallback
    show_snack(page, message)
    return True
