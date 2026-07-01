import flet as ft

import views.analisis_longitudinal as longitudinal_module


class FakePage:
    def __init__(self, width):
        self.width = width
        self.height = 844
        self.overlay = []
        self.snack_bar = None

    def update(self):
        pass


class FakeApiClient:
    def __init__(self, page):
        self.page = page

    def find_deportista_for_historial(self, query):
        return {"IDENTI_DEPORTISTA": "1001", "NOMBRE_DEPORTISTA": "Francisco Medina"}

    def get_historial_vista_all(self, identi):
        return [
            {"IDENTI_DEPORTISTA": identi, "FECHA_MEDIDA": "2026-01-01", "PESO_kg": 74, "IMC": 23, "PorcRasoYuasz": 12, "PorcGrasoFaulker": 14, "Mma": 36, "X": 1, "Y": 2},
            {"IDENTI_DEPORTISTA": identi, "FECHA_MEDIDA": "2026-06-01", "PESO_kg": 72, "IMC": 22, "PorcRasoYuasz": 11, "PorcGrasoFaulker": 13, "Mma": 37, "X": 2, "Y": 3},
        ]


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
    return [control.value for control in controls_in(root) if isinstance(control, ft.Text)]


def test_mobile_longitudinal_uses_compact_layout_separate_from_web(monkeypatch):
    monkeypatch.setattr(longitudinal_module, "ApiClient", FakeApiClient)
    view = longitudinal_module.AnalisisLongitudinalView(FakePage(390))

    assert "Datos del deportista" not in text_values(view)
    search = next(
        control for control in controls_in(view)
        if isinstance(control, ft.TextField) and control.hint_text == "Buscar deportista por nombre o ID"
    )
    search.value = "1001"
    search.on_submit(type("Event", (), {"control": search})())

    values = text_values(view)
    assert "Resumen longitudinal" in values
    assert "Evolución por variable" in values
    assert "Análisis de grasa: Yuhasz vs Faulkner" in values
    assert "Somatocarta longitudinal" in values
    assert "Comparación peso vs masa muscular" in values
    assert "Histórico de valoraciones" in values


def test_web_longitudinal_keeps_desktop_header(monkeypatch):
    monkeypatch.setattr(longitudinal_module, "ApiClient", FakeApiClient)
    view = longitudinal_module.AnalisisLongitudinalView(FakePage(1280))

    assert "Análisis Longitudinal" in text_values(view)
    assert "Datos del deportista" in text_values(view)
