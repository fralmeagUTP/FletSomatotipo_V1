from pathlib import Path


def source():
    return Path("views/historial.py").read_text(encoding="utf-8")


def test_historial_detail_does_not_create_nested_vertical_scrolls():
    text = source()

    assert "ft.Container(content=tabs, height=400)" not in text
    assert "ft.Container(content=tabs)" not in text
    assert "current_details_view = ft.ListView(spacing=14, expand=True)" in text
    assert "horizontal_alignment=ft.CrossAxisAlignment.STRETCH" in text


def test_historial_restores_useful_reference_sections():
    text = source()

    assert 'REFERENCE_IMAGES["imc"]' in text
    assert 'REFERENCE_IMAGES["contextura"]' in text
    assert 'REFERENCE_IMAGES["somatotipos"]' in text
    assert "build_reference_section(somatotipo, det)" in text


def test_historial_detail_uses_single_column_internal_layout():
    text = source()

    assert "width=float(\"inf\")" in text
    assert 'col={"xs": 12, "sm": 12, "md": 12, "lg": 12}' in text
    assert "ft.Row([image], scroll=ft.ScrollMode.AUTO)" not in text


def test_historial_detail_keeps_requested_section_order():
    text = source()

    lectura = text.index("build_reading_section(somatotipo, det)")
    medidas = text.index("build_measurement_section(det)", lectura)
    composicion = text.index('"Composición corporal"', lectura)
    referencias = text.index("build_reference_section(somatotipo, det)", composicion)
    somatotipo = text.index("build_somatotype_section(somatotipo, det)", referencias)

    assert lectura < medidas < composicion < referencias < somatotipo
    assert "build_detail_card" in text


def test_historial_somatotype_section_has_reference_without_duplicate_chips():
    text = source()

    assert '"Referencia de somatotipos corporales"' in text
    assert 'metric_card("Endomorfismo"' in text
    assert 'data_chip("Endomorfismo"' not in text
    assert "build_somatocarta_card" in text


def test_historial_measurements_show_correct_units():
    text = source()

    assert 'data_chip("Peso", det.get("PESO_kg"), "kg"' in text
    assert 'data_chip("Estatura", det.get("ESTA_USER_CM"), "cm"' in text
    assert 'data_chip("IMC", det.get("IMC"), "kg/m²"' in text
    assert 'data_chip("Tricipital", det.get("PLIEGUE_TRICIPITAL"), "mm")' in text
    assert 'data_chip("Carpo", det.get("CIRCUNFERENCIA_CARPO"), "cm")' in text
    assert 'data_chip("Pierna", det.get("PERIMETRO_PIERNA"), "cm")' in text


def test_historial_numeric_display_limits_to_two_decimals():
    text = source()

    assert 'return f"{numeric_value:.2f}".rstrip("0").rstrip(".")' in text
    assert 'return f"{display(value)} {unit}"' in text


def test_historial_has_no_mojibake_text():
    text = source()

    assert "\u00c3" not in text
    assert "\u00c2" not in text
    assert "\ufffd" not in text
    assert "Composici?" not in text
    assert "An?lisis" not in text


def test_historial_runs_search_and_pdf_downloads_off_ui_thread_when_available():
    text = source()

    assert "def run_search_historial" in text
    assert 'hasattr(page, "run_thread")' in text
    assert "download_pdf_sync" in text
