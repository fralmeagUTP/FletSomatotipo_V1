from pathlib import Path


def test_historial_detail_tabs_do_not_create_nested_vertical_scrolls():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    assert "ft.Container(content=tabs, height=400)" not in source
    assert "ft.Container(content=tabs)" not in source
    assert "current_details_view = ft.Column(scroll=ft.ScrollMode.AUTO)" in source
    assert "ft.Container(content=tabs, height=400)" not in source
    assert "ft.Container(content=tabs)" not in source


def test_historial_includes_reference_images_for_body_reading():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    assert 'REFERENCE_IMAGES["imc"]' in source
    assert 'REFERENCE_IMAGES["contextura"]' in source
    assert 'REFERENCE_IMAGES["somatotipos"]' in source


def test_historial_reference_images_are_readable_and_responsive():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    assert "width=float(\"inf\")" in source
    assert 'col={"xs": 12}' in source
    assert "page_width(page)" in source
    assert "aspect_ratio=0.79" in source
    assert "aspect_ratio=1.45" in source
    assert "fit=ft.ImageFit.CONTAIN" in source
    assert "ft.Row([image], scroll=ft.ScrollMode.AUTO)" not in source


def test_historial_detail_keeps_requested_section_order():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    medidas = source.index('ft.Text("Medidas"')
    composicion = source.index('ft.Text("Composición"')
    analisis = source.index('ft.Text("Análisis"')
    somatotipo = source.index('ft.Text("Somatotipo"')

    assert medidas < composicion < analisis < somatotipo
    assert "tabs.tabs[3].content" in source


def test_historial_measurements_show_units_in_values():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    for unit in ['"kg"', '"cm"', '"mm"', "'kg/m²'"]:
        assert unit in source
    assert "value_with_unit(det.get('PLIEGUE_TRICIPITAL'), \"mm\")" in source
    assert "value_with_unit(det.get('PERIMETRO_PIERNA'), \"cm\")" in source


def test_historial_has_no_mojibake_text():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    assert "\u00c3" not in source
    assert "\u00c2" not in source
    assert "\ufffd" not in source
    assert "Composici?" not in source
    assert "An?lisis" not in source


def test_historial_runs_search_and_pdf_downloads_off_ui_thread_when_available():
    source = Path("views/historial.py").read_text(encoding="utf-8")

    assert "def run_search_historial" in source
    assert 'hasattr(page, "run_thread")' in source
    assert "download_longitudinal_pdf_sync" in source
    assert "download_pdf_sync" in source
