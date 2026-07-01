import asyncio
from pathlib import Path

import flet as ft

import views.deportistas as deportistas_module


class FakePage:
    def __init__(self):
        self.width = 1280
        self.height = 800
        self.overlay = []
        self.services = []
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


def button_with_text(root, text):
    for control in controls_in(root):
        if not isinstance(control, (ft.ElevatedButton, ft.OutlinedButton, ft.TextButton)):
            continue
        content = getattr(control, "content", None)
        if content == text:
            return control
        if any(isinstance(child, ft.Text) and child.value == text for child in controls_in(content)):
            return control
    raise AssertionError(f"No se encontró el botón {text}")


def test_deportistas_view_builds_with_current_flet_api(monkeypatch):
    monkeypatch.setattr(deportistas_module, "ApiClient", FakeApiClient)
    page = FakePage()

    view = deportistas_module.DeportistasView(page)

    assert isinstance(view, ft.Container)
    assert not any(isinstance(control, ft.FilePicker) for control in page.overlay)
    assert any(isinstance(service, ft.FilePicker) for service in page.services)


def test_deportistas_registers_file_picker_as_service():
    source = open(deportistas_module.__file__, encoding="utf-8").read()

    assert "file_picker = ft.FilePicker()" in source
    assert "page.services.append(file_picker)" in source
    assert "page.overlay.append(file_picker)" not in source
    assert "ft.Tabs(" not in source
    assert "ft.TabBar(" not in source
    assert "form_content = ft.Column(" in source


def test_photo_button_reads_selected_image_bytes(monkeypatch):
    monkeypatch.setattr(deportistas_module, "ApiClient", FakeApiClient)
    page = FakePage()
    view = deportistas_module.DeportistasView(page)
    picker = next(service for service in page.services if isinstance(service, ft.FilePicker))

    async def fake_pick_files(**kwargs):
        assert kwargs["with_data"] is True
        assert kwargs["file_type"] == ft.FilePickerFileType.IMAGE
        return [ft.FilePickerFile(id=1, name="foto.jpg", size=4, bytes=b"foto")]

    monkeypatch.setattr(picker, "pick_files", fake_pick_files)
    controls = controls_in(view)
    add_button = next(control for control in controls if getattr(control, "content", None) == "Agregar Deportista")
    add_button.on_click(None)
    dialog_controls = controls_in(page.overlay)
    photo_button = next(
        control
        for control in dialog_controls
        if getattr(control, "content", None) == "Cargar o cambiar foto"
    )

    asyncio.run(photo_button.on_click(None))

    preview = next(control for control in dialog_controls if isinstance(control, ft.Image))
    assert preview.src == b"foto"
    assert any(isinstance(control, ft.Text) and control.value == "foto.jpg" for control in dialog_controls)


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


def test_mobile_crud_uses_four_step_athlete_form(monkeypatch):
    source = Path("views/deportistas.py").read_text(encoding="utf-8")

    assert "min_lines=4" in source
    assert "max_lines=6" in source
    assert "height=150" in source
    monkeypatch.setattr(deportistas_module, "ApiClient", FakeApiClient)
    page = FakePage()
    page.width = 390
    page.height = 844

    view = deportistas_module.DeportistasView(page)
    button_with_text(view, "Nuevo deportista").on_click(None)

    fields = {control.label: control for control in controls_in(view) if isinstance(control, (ft.TextField, ft.Dropdown))}
    assert "Tipo Documento" in fields
    assert "Identificación" in fields
    assert "Nombre Completo" in fields
    assert "Sexo" in fields

    fields["Tipo Documento"].value = "1"
    fields["Identificación"].value = "1001"
    fields["Nombre Completo"].value = "Deportista móvil"
    fields["Sexo"].value = "F"
    button_with_text(view, "Siguiente").on_click(None)

    labels = {control.label for control in controls_in(view) if isinstance(control, (ft.TextField, ft.Dropdown))}
    assert {"Teléfono", "Email", "País Nacimiento", "Depto Residencia", "Dirección"} <= labels
    button_with_text(view, "Siguiente").on_click(None)

    labels = {control.label for control in controls_in(view) if isinstance(control, (ft.TextField, ft.Dropdown))}
    assert {"Estrato", "Nivel Educativo", "Institución", "Observaciones"} <= labels
    button_with_text(view, "Siguiente").on_click(None)

    assert button_with_text(view, "Guardar")
    assert any(
        isinstance(control, ft.IconButton) and control.tooltip == "Seleccionar foto"
        for control in controls_in(view)
    )
