from pathlib import Path

import flet as ft

from app_config import is_web_runtime


async def _save_web_pdf(file_picker, pdf_bytes: bytes, filename: str):
    await file_picker.save_file(file_name=filename, src_bytes=pdf_bytes)


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

    target_dir = Path(output_dir) if output_dir else Path.home() / "Downloads"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(pdf_bytes)
    if hasattr(page, "launch_url"):
        page.launch_url(target_path.as_uri())
    return target_path
