import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import flet as ft
from fastapi.testclient import TestClient

import web_main
from src.frontend.assets import ASSETS_DIR
from src.frontend.runtime import _save_web_pdf, deliver_pdf


class FakePage:
    def __init__(self, web=False):
        self.web = web
        self.launched_urls = []
        self.services = []
        self.tasks = []
        self.updated = 0

    def launch_url(self, url):
        self.launched_urls.append(url)

    def update(self):
        self.updated += 1

    def run_task(self, handler, *args):
        self.tasks.append((handler, args))


class FletWebTests(unittest.TestCase):
    def test_web_entry_uses_shared_main_and_assets(self):
        with patch("web_main.ft.run") as run:
            web_main.run_web()

        kwargs = run.call_args.kwargs
        self.assertIs(run.call_args.args[0], web_main.main)
        self.assertEqual(kwargs["view"], ft.AppView.WEB_BROWSER)
        self.assertEqual(kwargs["assets_dir"], "assets")
        self.assertGreater(kwargs["port"], 0)

    def test_web_asgi_factory_serves_browser_shell(self):
        app = web_main.create_web_app()

        response = TestClient(app).get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("<html", response.text.lower())

    def test_web_asgi_serves_every_mobile_visual_asset(self):
        client = TestClient(web_main.create_web_app())

        for asset in ASSETS_DIR.iterdir():
            if not asset.is_file():
                continue
            response = client.get(f"/{asset.name}")
            self.assertEqual(response.status_code, 200, asset.name)
            self.assertEqual(response.content, asset.read_bytes(), asset.name)

    def test_web_pdf_is_opened_without_writing_server_file(self):
        page = FakePage(web=True)
        payload = b"%PDF-1.4\nweb"

        result = deliver_pdf(page, payload, "informe.pdf")

        self.assertEqual(result, "informe.pdf")
        self.assertEqual(len(page.services), 1)
        self.assertEqual(page.updated, 1)
        self.assertEqual(page.tasks[0][0], _save_web_pdf)
        self.assertEqual(page.tasks[0][1][1:], (payload, "informe.pdf"))
        self.assertEqual(page.launched_urls, [])

    def test_web_pdf_service_passes_bytes_to_file_picker(self):
        file_picker = AsyncMock()

        asyncio.run(_save_web_pdf(file_picker, b"%PDF", "informe.pdf"))

        file_picker.save_file.assert_awaited_once_with(
            file_name="informe.pdf",
            src_bytes=b"%PDF",
        )

    def test_native_pdf_is_saved_and_opened(self):
        page = FakePage(web=False)
        payload = b"%PDF-1.4\nnative"

        with tempfile.TemporaryDirectory() as directory:
            result = deliver_pdf(page, payload, "informe.pdf", directory)

            self.assertEqual(result, Path(directory) / "informe.pdf")
            self.assertEqual(result.read_bytes(), payload)
            self.assertEqual(page.launched_urls, [result.as_uri()])

    def test_invalid_pdf_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PDF válido"):
            deliver_pdf(FakePage(web=True), b"not-pdf", "informe.pdf")


if __name__ == "__main__":
    unittest.main()
