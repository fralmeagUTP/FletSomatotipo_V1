import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import flet as ft
from fastapi.testclient import TestClient

import web_main
from src.frontend.assets import ASSETS_DIR
from src.frontend.runtime import _open_file_external, _save_web_pdf, _share_native_pdf, deliver_pdf, share_pdf


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

        with tempfile.TemporaryDirectory() as directory, patch("src.frontend.runtime._open_file_external") as opener:
            result = deliver_pdf(page, payload, "informe.pdf", directory)

            self.assertEqual(result, Path(directory) / "informe.pdf")
            self.assertEqual(result.read_bytes(), payload)
            opener.assert_called_once_with(result, page)

    def test_android_pdf_is_saved_in_public_downloads(self):
        page = FakePage(web=False)
        payload = b"%PDF-1.4\nandroid"

        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {"ANDROID_ROOT": "/system", "SOMATOCARTA_ANDROID_DOWNLOADS": directory},
        ), patch("src.frontend.runtime._open_file_external") as opener:
            result = deliver_pdf(page, payload, "informe.pdf")

            self.assertEqual(result, Path(directory) / "informe.pdf")
            self.assertEqual(result.read_bytes(), payload)
            opener.assert_called_once_with(result, page)

    def test_android_pdf_uses_external_pdf_intent(self):
        page = FakePage(web=False)

        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {"ANDROID_ROOT": "/system"},
        ), patch("src.frontend.runtime.subprocess.Popen") as popen:
            path = Path(directory) / "informe.pdf"
            path.write_bytes(b"%PDF-1.4")

            self.assertTrue(_open_file_external(path, page))

            command = popen.call_args.args[0]
            self.assertIn("android.intent.action.VIEW", command)
            self.assertIn("application/pdf", command)
            self.assertIn(path.as_uri(), command)
            self.assertEqual(page.launched_urls, [])

    def test_native_share_service_receives_pdf_bytes_and_metadata(self):
        share_service = AsyncMock()

        asyncio.run(_share_native_pdf(share_service, b"%PDF-1.4", "informe.pdf"))

        share_service.share_files.assert_awaited_once()
        files = share_service.share_files.await_args.args[0]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].data, b"%PDF-1.4")
        self.assertEqual(files[0].mime_type, "application/pdf")
        self.assertEqual(files[0].name, "informe.pdf")

    def test_share_pdf_registers_native_service_and_schedules_share_sheet(self):
        page = FakePage(web=False)
        payload = b"%PDF-1.4\nandroid"
        share_service = object()

        with patch.dict(
            "os.environ",
            {"ANDROID_ROOT": "/system"},
        ), patch("src.frontend.runtime.ft.Share", return_value=share_service):
            result = share_pdf(page, payload, "informe.pdf")

        self.assertEqual(result, "informe.pdf")
        self.assertEqual(page.services, [share_service])
        self.assertEqual(page.updated, 1)
        self.assertEqual(page.tasks, [(_share_native_pdf, (share_service, payload, "informe.pdf"))])

    def test_native_pdf_falls_back_to_launch_url_when_no_system_opener_exists(self):
        page = FakePage(web=False)

        with tempfile.TemporaryDirectory() as directory, patch("src.frontend.runtime.platform.system", return_value="Linux"), patch.dict("os.environ", {"ANDROID_ROOT": "/system"}), patch("src.frontend.runtime._open_android_pdf", return_value=False):
            path = Path(directory) / "informe.pdf"
            path.write_bytes(b"%PDF-1.4")

            self.assertTrue(_open_file_external(path, page))
            self.assertEqual(page.launched_urls, [path.as_uri()])

    def test_invalid_pdf_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PDF válido"):
            deliver_pdf(FakePage(web=True), b"not-pdf", "informe.pdf")


if __name__ == "__main__":
    unittest.main()
