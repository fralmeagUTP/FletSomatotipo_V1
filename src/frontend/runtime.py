import os
import platform
import subprocess
from pathlib import Path
from urllib.parse import quote

import flet as ft

from app_config import is_web_runtime


async def _save_web_pdf(file_picker, pdf_bytes: bytes, filename: str):
    await file_picker.save_file(file_name=filename, src_bytes=pdf_bytes)


def _is_android_runtime() -> bool:
    return bool(os.getenv("ANDROID_ROOT") or os.getenv("ANDROID_DATA"))


def _android_downloads_dir() -> Path | None:
    override = os.getenv("SOMATOCARTA_ANDROID_DOWNLOADS")
    candidates = [
        override,
        "/storage/emulated/0/Download",
        "/sdcard/Download",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        try:
            path.mkdir(parents=True, exist_ok=True)
            if path.exists():
                return path
        except Exception:
            continue
    return None


def _default_pdf_dir() -> Path:
    if _is_android_runtime():
        android_dir = _android_downloads_dir()
        if android_dir is not None:
            return android_dir
    return Path.home() / "Downloads"


def _open_android_pdf(path: Path) -> bool:
    uri = path.as_uri()
    commands = [
        [
            "/system/bin/am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-t",
            "application/pdf",
            "-d",
            uri,
        ],
        [
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-t",
            "application/pdf",
            "-d",
            uri,
        ],
    ]
    for command in commands:
        try:
            subprocess.Popen(command)
            return True
        except Exception:
            continue
    return False


def _android_content_uri(path: Path) -> str:
    authority = os.getenv("SOMATOCARTA_ANDROID_FILE_PROVIDER", "com.nyquist.somatocarta.provider")
    normalized = str(path).replace("\\", "/")
    for root in ("/storage/emulated/0/", "/sdcard/"):
        if normalized.startswith(root):
            relative_path = normalized[len(root):]
            return f"content://{authority}/external_files/{quote(relative_path, safe='/')}"
    return path.as_uri()


def _share_android_pdf(path: Path) -> bool:
    uri = _android_content_uri(path)
    commands = [
        [
            executable,
            "start",
            "-a",
            "android.intent.action.SEND",
            "-t",
            "application/pdf",
            "--eu",
            "android.intent.extra.STREAM",
            uri,
            "-f",
            "0x00000001",
        ]
        for executable in ("/system/bin/am", "am")
    ]
    for command in commands:
        try:
            subprocess.Popen(command)
            return True
        except Exception:
            continue
    return False


def _open_file_external(path: Path, page=None) -> bool:
    try:
        if _is_android_runtime() and _open_android_pdf(path):
            return True
        if platform.system() == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
            return True
        if platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
            return True
        if platform.system() == "Linux" and not _is_android_runtime():
            subprocess.Popen(["xdg-open", str(path)])
            return True
    except Exception:
        pass

    if page is not None and hasattr(page, "launch_url"):
        page.launch_url(path.as_uri())
        return True
    return False


def deliver_pdf(page, pdf_bytes: bytes, filename: str, output_dir: str | Path | None = None):
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("El servidor no devolvió un PDF válido.")

    if is_web_runtime(page):
        file_picker = getattr(page, "_somatocarta_pdf_picker", None)
        if file_picker is None:
            file_picker = ft.FilePicker()
            page.services.append(file_picker)
            page._somatocarta_pdf_picker = file_picker
            page.update()
        page.run_task(_save_web_pdf, file_picker, pdf_bytes, filename)
        return filename

    target_dir = Path(output_dir) if output_dir else _default_pdf_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(pdf_bytes)
    _open_file_external(target_path, page)
    return target_path


def share_pdf(page, pdf_bytes: bytes, filename: str, output_dir: str | Path | None = None):
    if not _is_android_runtime():
        return deliver_pdf(page, pdf_bytes, filename, output_dir)
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("El servidor no devolvió un PDF válido.")

    target_dir = Path(output_dir) if output_dir else _default_pdf_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(pdf_bytes)
    if not _share_android_pdf(target_path):
        _open_file_external(target_path, page)
    return target_path
