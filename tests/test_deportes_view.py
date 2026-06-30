import flet as ft

import views.deportes as deportes_module


class FakePage:
    def __init__(self):
        self.width = 390
        self.height = 844
        self.overlay = []
        self.snack_bar = None

    def update(self):
        pass

    def open(self, control):
        if control not in self.overlay:
            self.overlay.append(control)
        control.open = True

    def close(self, control):
        control.open = False


class FakeApiClient:
    created = []
    updated = []
    deleted = []

    def __init__(self, page):
        self.page = page

    def list_deportes_page(self, search="", page=1, page_size=50):
        return {
            "items": [{"ID_DEPORTE": 6, "DEPORTE": "Natación"}],
            "total": 1,
            "page": page,
            "page_size": page_size,
        }

    def create_deporte(self, payload):
        self.created.append(payload)

    def update_deporte(self, deporte_id, payload):
        self.updated.append((deporte_id, payload))

    def delete_deporte(self, deporte_id):
        self.deleted.append(deporte_id)


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


def text_values(root):
    return {control.value for control in controls_in(root) if isinstance(control, ft.Text)}


def clickable_containing(root, text):
    return next(
        control
        for control in controls_in(root)
        if isinstance(control, ft.Container) and control.on_click and text in text_values(control)
    )


def button_with_text(root, text):
    return next(
        control
        for control in controls_in(root)
        if isinstance(control, (ft.ElevatedButton, ft.TextButton))
        and (control.content == text or text in text_values(control.content))
    )


def test_mobile_deportes_shows_names_and_runs_crud(monkeypatch):
    FakeApiClient.created = []
    FakeApiClient.updated = []
    FakeApiClient.deleted = []
    monkeypatch.setattr(deportes_module, "ApiClient", FakeApiClient)
    page = FakePage()

    view = deportes_module.DeportesView(page)

    assert "Natación" in text_values(view)
    assert "ID: 6" in text_values(view)

    button_with_text(view, "Agregar deporte").on_click(None)
    dialog = next(control for control in page.overlay if isinstance(control, ft.AlertDialog) and control.open)
    fields = {control.label: control for control in controls_in(dialog) if isinstance(control, ft.TextField)}
    fields["Nombre del deporte"].value = "Ciclismo"
    button_with_text(dialog, "Guardar").on_click(None)
    assert FakeApiClient.created == [{"ID_DEPORTE": None, "DEPORTE": "Ciclismo"}]

    clickable_containing(view, "Natación").on_click(None)
    dialog = next(control for control in page.overlay if isinstance(control, ft.AlertDialog) and control.open)
    fields = {control.label: control for control in controls_in(dialog) if isinstance(control, ft.TextField)}
    fields["Nombre del deporte"].value = "Natación carreras"
    button_with_text(dialog, "Guardar").on_click(None)
    assert FakeApiClient.updated[-1] == (6, {"ID_DEPORTE": 6, "DEPORTE": "Natación carreras"})

    clickable_containing(view, "Natación").on_click(None)
    dialog = next(control for control in page.overlay if isinstance(control, ft.AlertDialog) and control.open)
    button_with_text(dialog, "Eliminar").on_click(None)
    confirmation = next(
        control
        for control in page.overlay
        if isinstance(control, ft.AlertDialog)
        and control.open
        and isinstance(control.title, ft.Text)
        and control.title.value == "Eliminar deporte"
    )
    button_with_text(confirmation, "Eliminar").on_click(None)
    assert FakeApiClient.deleted == [6]
