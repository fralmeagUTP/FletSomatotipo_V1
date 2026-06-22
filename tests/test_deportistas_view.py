import flet as ft

import views.deportistas as deportistas_module


class FakePage:
    def __init__(self):
        self.width = 1280
        self.height = 800
        self.overlay = []
        self.snack_bar = None
        self.updated = 0

    def update(self):
        self.updated += 1

    def open(self, control):
        pass

    def close(self, control):
        pass


class FakeApiClient:
    items = []
    deleted = []

    def __init__(self, page):
        self.page = page

    def get_catalogs(self):
        return {
            "tipos_documentos": [],
            "estratos": [],
            "niveles_educativos": [],
        }

    def list_deportistas_page(self, search="", page=1, page_size=50):
        return {"items": self.items, "total": len(self.items), "page": page, "page_size": page_size}

    def delete_deportista(self, athlete_id):
        self.deleted.append(athlete_id)


def controls_in(root):
    seen = set()

    def walk(value):
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, ft.Control):
            yield value
            for child in vars(value).values():
                yield from walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                yield from walk(child)
        elif isinstance(value, dict):
            for child in value.values():
                yield from walk(child)

    return list(walk(root))


def test_deportistas_view_builds_with_current_flet_api(monkeypatch):
    monkeypatch.setattr(deportistas_module, "ApiClient", FakeApiClient)
    page = FakePage()

    view = deportistas_module.DeportistasView(page)

    assert isinstance(view, ft.Container)
    assert not any(isinstance(control, ft.FilePicker) for control in page.overlay)


def test_deportistas_avoids_runtime_incompatible_controls():
    source = open(deportistas_module.__file__, encoding="utf-8").read()

    assert "ft.FilePicker(" not in source
    assert "ft.Tabs(" not in source
    assert "ft.TabBar(" not in source
    assert "form_content = ft.Column(" in source


def test_add_edit_and_delete_buttons_open_their_dialogs(monkeypatch):
    athlete = {
        "IDENTI_DEPORTISTA": "1001",
        "TIPO_IDENTI": None,
        "NOMBRE_DEPORTISTA": "Deportista de prueba",
        "SEXO_DEPORTISTA": "F",
        "FECHA_NAC": "2000-01-01",
        "FOTO_DEPORTISTA": None,
        "PAIS_NAC": None,
        "DEPARTA_NAC": None,
        "CIUDAD_NAC": None,
        "DEPARTA_RESI": None,
        "CIUDAD_RESI": None,
        "DIRECC_RESI": None,
        "TELEFONO": None,
        "E_MAIL": None,
        "ID_ESTRATO": None,
        "ID_NIVEL": None,
        "NOMBRE_INSTITU": None,
        "OBSERVACIONES": None,
    }
    monkeypatch.setattr(FakeApiClient, "items", [athlete])
    monkeypatch.setattr(FakeApiClient, "deleted", [])
    monkeypatch.setattr(deportistas_module, "ApiClient", FakeApiClient)
    page = FakePage()
    view = deportistas_module.DeportistasView(page)
    controls = controls_in(view)

    add_button = next(control for control in controls if getattr(control, "content", None) == "Agregar Deportista")
    edit_button = next(control for control in controls if getattr(control, "tooltip", None) == "Editar")
    delete_button = next(control for control in controls if getattr(control, "tooltip", None) == "Eliminar")

    add_button.on_click(None)
    assert any(isinstance(control, ft.AlertDialog) and control.open for control in page.overlay)

    for control in page.overlay:
        if isinstance(control, ft.AlertDialog):
            control.open = False
    edit_button.on_click(None)
    assert any(isinstance(control, ft.AlertDialog) and control.open for control in page.overlay)

    for control in page.overlay:
        if isinstance(control, ft.AlertDialog):
            control.open = False
    delete_button.on_click(None)
    assert any(isinstance(control, ft.AlertDialog) and control.open for control in page.overlay)

    confirm_delete = next(
        control
        for control in controls_in(page.overlay)
        if getattr(control, "content", None) == "Eliminar"
    )
    confirm_delete.on_click(None)
    assert FakeApiClient.deleted == ["1001"]
