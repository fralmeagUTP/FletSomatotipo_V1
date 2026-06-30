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
