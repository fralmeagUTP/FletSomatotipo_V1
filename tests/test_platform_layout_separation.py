from pathlib import Path


def test_mobile_specific_views_use_platform_aware_layout_selector():
    views = (
        "views/dashboard.py",
        "views/deportistas.py",
        "views/deportes.py",
        "views/entidades.py",
        "views/asignaciones.py",
        "views/valoracion.py",
        "views/historial.py",
        "views/analisis_longitudinal.py",
        "views/acerca.py",
    )

    for filename in views:
        source = Path(filename).read_text(encoding="utf-8")
        assert "is_mobile" in source, filename


def test_web_entry_explicitly_marks_web_runtime():
    source = Path("web_main.py").read_text(encoding="utf-8")

    assert 'os.environ["APP_RUNTIME"] = "web"' in source
