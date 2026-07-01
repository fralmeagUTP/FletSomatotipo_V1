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


def test_login_uses_the_same_platform_aware_layout_selector():
    source = Path("main.py").read_text(encoding="utf-8")

    assert "is_mobile_layout = uses_mobile_app_layout(page)" in source
    assert 'is_mobile_layout = (getattr(page, "width", None) or 390) < 700' not in source
