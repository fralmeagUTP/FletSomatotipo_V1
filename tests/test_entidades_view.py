import flet as ft

import views.entidades as entidades_module


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

    def list_entidades_page(self, search="", page=1, page_size=10):
        return {
            "items": [{
                "NIT_ENTIDAD": "900",
                "RAZON_SOCIAL": "Universidad Tecnológica de Pereira",
                "TELEFONO": "6063137300",
                "CONTACTO": "Bienestar Universitario",
                "E_MAIL": "bienestar@utp.edu.co",
            }],
            "total": 1,
            "page": page,
            "page_size": page_size,
        }

    def create_entidad(self, payload):
        self.created.append(payload)

    def update_entidad(self, nit, payload):
        self.updated.append((nit, payload))

    def delete_entidad(self, nit):
        self.deleted.append(nit)


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


def texts(root):
    return {control.value for control in controls_in(root) if isinstance(control, ft.Text)}


def button(root, label):
    return next(
        control for control in controls_in(root)
        if isinstance(control, (ft.ElevatedButton, ft.TextButton))
        and (control.content == label or label in texts(control.content))
    )


def dialog(page, title):
    return next(
        control for control in page.overlay
        if isinstance(control, ft.AlertDialog)
        and control.open
        and isinstance(control.title, ft.Text)
        and control.title.value == title
    )


def entity_card(root):
    return next(
        control for control in controls_in(root)
        if isinstance(control, ft.Container)
        and control.on_click
        and "Universidad Tecnológica de Pereira" in texts(control)
    )


def test_mobile_entidades_uses_consistent_design_and_runs_crud(monkeypatch):
    FakeApiClient.created = []
    FakeApiClient.updated = []
    FakeApiClient.deleted = []
    monkeypatch.setattr(entidades_module, "ApiClient", FakeApiClient)
    page = FakePage()

    view = entidades_module.EntidadesView(page)
    assert "Universidad Tecnológica de Pereira" in texts(view)
    assert "NIT: 900" in texts(view)

    button(view, "Agregar entidad").on_click(None)
    form = dialog(page, "Nueva entidad")
    fields = {control.label: control for control in controls_in(form) if isinstance(control, ft.TextField)}
    fields["NIT entidad"].value = "901"
    fields["Razón social"].value = "Liga Deportiva"
    button(form, "Guardar").on_click(None)
    assert FakeApiClient.created[-1]["RAZON_SOCIAL"] == "Liga Deportiva"

    entity_card(view).on_click(None)
    form = dialog(page, "Editar entidad")
    fields = {control.label: control for control in controls_in(form) if isinstance(control, ft.TextField)}
    fields["Contacto"].value = "Deportes"
    button(form, "Guardar").on_click(None)
    assert FakeApiClient.updated[-1][0] == "900"
    assert FakeApiClient.updated[-1][1]["CONTACTO"] == "Deportes"

    entity_card(view).on_click(None)
    form = dialog(page, "Editar entidad")
    button(form, "Eliminar").on_click(None)
    confirmation = dialog(page, "Eliminar entidad")
    button(confirmation, "Eliminar").on_click(None)
    assert FakeApiClient.deleted == ["900"]
