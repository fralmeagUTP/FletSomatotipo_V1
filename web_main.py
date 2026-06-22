import os

import flet as ft

from app_config import WEB_HOST, WEB_PORT
from main import main


def create_web_app():
    os.environ["APP_RUNTIME"] = "web"
    return ft.run(
        main,
        assets_dir="assets",
        export_asgi_app=True,
    )


def run_web():
    os.environ["APP_RUNTIME"] = "web"
    ft.run(
        main,
        host=WEB_HOST,
        port=WEB_PORT,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
    )


if __name__ == "__main__":
    run_web()
