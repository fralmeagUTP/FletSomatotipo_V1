from pathlib import Path


def test_dashboard_redesign_contains_required_operational_sections():
    source = Path("views/dashboard.py").read_text(encoding="utf-8")

    required_text = [
        "Nueva valoración",
        "Operación y análisis",
        "Gestión de datos",
        "Sistema",
        "Acerca del proyecto",
        "Análisis longitudinal",
    ]

    for text in required_text:
        assert text in source

    assert "Actividad reciente" not in source
    assert "Vista SQL" not in source


def test_global_shell_contains_required_navigation_entries():
    source = Path("src/frontend/app_shell.py").read_text(encoding="utf-8")

    required_text = [
        "Valoración corporal",
        "Deportistas",
        "Análisis de valoración corporal",
        "Análisis longitudinal",
        "Deportes",
        "Entidades",
        "Asignaciones",
        "Acerca del proyecto",
        "Cerrar sesión",
        "Buscar deportista por nombre o ID",
    ]

    for text in required_text:
        assert text in source


def test_global_search_dialog_uses_robust_close_handler():
    source = Path("src/frontend/app_shell.py").read_text(encoding="utf-8")

    assert "def close_overlay" in source
    assert "on_click=close_search_dialog" in source
    assert "ft.Icons.CLOSE" in source
    assert "navigate_from_result" in source
