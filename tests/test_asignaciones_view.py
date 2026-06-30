import flet as ft

import views.asignaciones as asignaciones_module


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

    def list_deportes(self, **_):
        return [{"ID_DEPORTE": 6, "DEPORTE": "Natación"}]

    def list_entidades(self, **_):
        return [{"NIT_ENTIDAD": "900", "RAZON_SOCIAL": "Universidad Tecnológica de Pereira"}]

    def list_deportistas(self, *_):
        return [{
            "IDENTI_DEPORTISTA": "1001",
            "NOMBRE_DEPORTISTA": "Francisco Medina",
            "FECHA_NAC": "1990-06-15",
            "E_MAIL": "francisco@example.com",
            "CIUDAD_RESI": "Pereira",
            "DEPARTA_RESI": "Risaralda",
            "DIRECC_RESI": "Carrera 10 # 20-30",
        }]

    def list_asignaciones_page(self, search="", page=1, page_size=10):
        return {
            "items": [{
                "id": 4,
                "ID_DEPORTE": 6,
                "IDENTI_DEPORTISTA": "1001",
                "NIT_ENTIDAD": "900",
                "NOMBRE_DEPORTISTA": "Francisco Medina",
                "DEPORTE": "Natación",
                "RAZON_SOCIAL": "Universidad Tecnológica de Pereira",
            }],
            "total": 1,
            "page": page,
            "page_size": page_size,
        }

    def create_asignacion(self, payload):
        self.created.append(payload)

    def update_asignacion(self, assignment_id, payload):
        self.updated.append((assignment_id, payload))

    def delete_asignacion(self, assignment_id):
        self.deleted.append(assignment_id)


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


def button_with_text(root, text):
    return next(
        control for control in controls_in(root)
        if isinstance(control, (ft.ElevatedButton, ft.TextButton))
        and (control.content == text or text in text_values(control.content))
    )


def assignment_card(root):
    return next(
        control for control in controls_in(root)
        if isinstance(control, ft.Container)
        and control.on_click
        and "Francisco Medina" in text_values(control)
    )


def open_dialog(page, title):
    return next(
        control for control in page.overlay
        if isinstance(control, ft.AlertDialog)
        and control.open
        and isinstance(control.title, ft.Text)
        and control.title.value == title
    )


def test_mobile_asignaciones_matches_list_design_and_runs_crud(monkeypatch):
    FakeApiClient.created = []
    FakeApiClient.updated = []
    FakeApiClient.deleted = []
    monkeypatch.setattr(asignaciones_module, "ApiClient", FakeApiClient)
    page = FakePage()

    view = asignaciones_module.AsignacionesView(page)

    assert "Francisco Medina" in text_values(view)
    assert "Natación · Universidad Tecnológica de Pereira" in text_values(view)

    button_with_text(view, "Nueva asignación").on_click(None)
    dialog = open_dialog(page, "Nueva asignación")
    athlete_search = next(control for control in controls_in(dialog) if isinstance(control, ft.TextField))
    athlete_search.value = "1001"
    athlete_search.on_submit(None)
    dropdowns = [control for control in controls_in(dialog) if isinstance(control, ft.Dropdown)]
    dropdowns[0].value = "6"
    dropdowns[1].value = "900"
    button_with_text(dialog, "Guardar").on_click(None)
    expected = {"ID_DEPORTE": 6, "IDENTI_DEPORTISTA": "1001", "NIT_ENTIDAD": "900"}
    assert FakeApiClient.created == [expected]

    assignment_card(view).on_click(None)
    dialog = open_dialog(page, "Editar asignación")
    assert "Email: francisco@example.com" in text_values(dialog)
    assert "Ubicación: Pereira, Risaralda" in text_values(dialog)
    assert "Dirección: Carrera 10 # 20-30" in text_values(dialog)
    button_with_text(dialog, "Guardar").on_click(None)
    assert FakeApiClient.updated[-1] == (4, expected)

    assignment_card(view).on_click(None)
    dialog = open_dialog(page, "Editar asignación")
    button_with_text(dialog, "Eliminar").on_click(None)
    confirmation = open_dialog(page, "Eliminar asignacion")
    button_with_text(confirmation, "Eliminar").on_click(None)
    assert FakeApiClient.deleted == [4]
