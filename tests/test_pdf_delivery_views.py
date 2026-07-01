from pathlib import Path


def test_historial_and_longitudinal_pdf_buttons_use_external_delivery_helper():
    historial = Path("views/historial.py").read_text(encoding="utf-8")
    longitudinal = Path("views/analisis_longitudinal.py").read_text(encoding="utf-8")

    assert "from src.frontend.runtime import deliver_pdf" in historial
    assert "delivery = share_pdf if mobile_mode else deliver_pdf" in historial
    assert "target = delivery(" in historial
    assert "get_somatotipo_pdf_bytes" in historial
    assert "valoracion_{somatotipo_id}.pdf" in historial

    assert "from src.frontend.runtime import deliver_pdf" in longitudinal
    assert "delivery = share_pdf if mobile_mode else deliver_pdf" in longitudinal
    assert "target = delivery(" in longitudinal
    assert "get_longitudinal_pdf_bytes" in longitudinal
    assert "analisis_longitudinal_{identi}.pdf" in longitudinal


def test_mobile_pdf_buttons_share_the_same_component():
    historial = Path("views/historial.py").read_text(encoding="utf-8")
    longitudinal = Path("views/analisis_longitudinal.py").read_text(encoding="utf-8")

    assert "pdf_button = pdf_action_button(download_pdf, mobile=mobile_mode)" in historial
    assert "download_button = pdf_action_button(download_pdf, mobile=mobile_mode" in longitudinal
    assert "pdf_action_button(download_pdf, mobile=True)" in longitudinal


def test_android_pdf_share_uses_flet_native_share_service():
    runtime = Path("src/frontend/runtime.py").read_text(encoding="utf-8")

    assert "ft.Share()" in runtime
    assert "ft.ShareFile.from_path" in runtime
    assert 'Path(tempfile.gettempdir()) / "somatocarta-share"' in runtime
    assert "share_service.share_files" in runtime
    assert "android.intent.action.SEND" not in runtime
