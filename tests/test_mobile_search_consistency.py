from pathlib import Path


def test_main_mobile_views_use_shared_search_component():
    expected_views = (
        "views/deportes.py",
        "views/entidades.py",
        "views/asignaciones.py",
        "views/deportistas.py",
        "views/historial.py",
        "views/analisis_longitudinal.py",
        "views/valoracion.py",
    )

    for filename in expected_views:
        source = Path(filename).read_text(encoding="utf-8")
        assert "mobile_search_field(" in source, filename


def test_mobile_crud_create_action_follows_search_field():
    expected_actions = {
        "views/deportes.py": 'mobile_primary_button("Agregar deporte"',
        "views/entidades.py": 'mobile_primary_button("Agregar entidad"',
        "views/asignaciones.py": 'mobile_primary_button("Nueva asignación"',
        "views/deportistas.py": 'mobile_primary_button("Nuevo deportista"',
    }

    for filename, action in expected_actions.items():
        source = Path(filename).read_text(encoding="utf-8")
        mobile_layout = source[source.index("if is_mobile(page):") :] if "if is_mobile(page):" in source else source
        search_position = mobile_layout.find("mobile_search")
        action_position = mobile_layout.find(action)
        assert search_position >= 0, filename
        assert action_position > search_position, filename
