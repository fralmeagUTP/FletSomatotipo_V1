import unittest

import flet as ft

import views.valoracion as valoracion_module


class FakeSession:
    def __init__(self):
        self.data = {"login_user": "tester"}

    def get(self, key):
        return self.data.get(key)


class FakePage:
    def __init__(self):
        self.width = 1280
        self.height = 800
        self.session = FakeSession()
        self.snack_bar = None
        self.updated = 0
        self.overlay = []

    def update(self):
        self.updated += 1

    def open(self, control):
        pass

    def close(self, control):
        pass


class FakeApiClient:
    calls = []
    athletes = []
    created_payloads = []
    editable_records = []
    loaded_records = {}
    updated_details = []
    deleted_ids = []
    created_details = []
    deleted_detail_ids = []

    def __init__(self, page):
        self.page = page

    def list_deportistas(self, search="", page=1, page_size=50):
        self.__class__.calls.append(("list_deportistas", search, page, page_size))
        return self.__class__.athletes

    def create_somatotipo(self, payload):
        self.__class__.created_payloads.append(payload)
        return {"id_Somatotipo": 1}

    def list_somatotipos_editables(self, identi):
        self.__class__.calls.append(("list_somatotipos_editables", identi))
        return self.__class__.editable_records

    def get_somatotipo_editable(self, somatotipo_id):
        self.__class__.calls.append(("get_somatotipo_editable", somatotipo_id))
        return self.__class__.loaded_records.get(somatotipo_id, self.__class__.editable_records[0])

    def update_somatotipo_detalle(self, detail_id, data):
        self.__class__.updated_details.append((detail_id, data))
        updated = dict(data)
        updated["ID"] = detail_id
        updated["id_Somatotipo"] = 10
        return updated

    def create_somatotipo_detalle(self, somatotipo_id, data):
        self.__class__.created_details.append((somatotipo_id, data))
        created = dict(data)
        created["ID"] = 88
        created["id_Somatotipo"] = somatotipo_id
        return created

    def delete_somatotipo_detalle(self, detail_id):
        self.__class__.deleted_detail_ids.append(detail_id)
        return {"message": "ok", "ID": detail_id}

    def delete_somatotipo(self, somatotipo_id):
        self.__class__.deleted_ids.append(somatotipo_id)
        return {"message": "ok"}


def walk_controls(control):
    yield control
    for attr in ("content",):
        child = getattr(control, attr, None)
        if child is not None:
            yield from walk_controls(child)
    for attr in ("controls", "rows", "cells"):
        children = getattr(control, attr, None) or []
        for child in children:
            yield from walk_controls(child)


def find_text_field(root, label):
    for control in walk_controls(root):
        if isinstance(control, ft.TextField) and control.label == label:
            return control
    raise AssertionError(f"No se encontró TextField con label {label!r}")


def find_button(root, text):
    for control in walk_controls(root):
        if isinstance(control, (ft.ElevatedButton, ft.OutlinedButton, ft.Button)) and control.text == text:
            return control
    raise AssertionError(f"No se encontró botón {text!r}")


class ValoracionViewTests(unittest.TestCase):
    def setUp(self):
        self.original_api_client = valoracion_module.ApiClient
        self.original_show_dashboard = valoracion_module.show_dashboard
        valoracion_module.ApiClient = FakeApiClient
        valoracion_module.show_dashboard = lambda page: None
        FakeApiClient.calls = []
        FakeApiClient.created_payloads = []
        FakeApiClient.updated_details = []
        FakeApiClient.deleted_ids = []
        FakeApiClient.created_details = []
        FakeApiClient.deleted_detail_ids = []
        FakeApiClient.editable_records = []
        FakeApiClient.loaded_records = {}
        FakeApiClient.athletes = [
            {
                "IDENTI_DEPORTISTA": "1001",
                "NOMBRE_DEPORTISTA": "Estudiante 1",
                "FECHA_NAC": "2007-01-01",
                "CIUDAD_RESI": "Pereira",
                "NOMBRE_INSTITU": "CDR",
                "E_MAIL": "estudiante@example.com",
            }
        ]
        self.page = FakePage()
        self.view = valoracion_module.ValoracionView(self.page)

    def stored_record(self):
        return {
            "id_Somatotipo": 10,
            "IDENTI_DEPORTISTA": "1001",
            "FECHA_MEDIDA": "2026-06-08",
            "OBSERVACIONES": "Control",
            "DETALLES": [
                {
                    "ID": 77,
                    "id_Somatotipo": 10,
                    "ESTA_USER_CM": 170.0,
                    "PESO_kg": 65.0,
                    "PLIEGUE_TRICIPITAL": 10.0,
                    "PLIEGUE_SUBESCAPULAR": 9.0,
                    "PLIEGUE_SUPRAILIACO": 11.0,
                    "PLIEGUE_ABDOMINAL": 16.0,
                    "PLIEGUE_MUSLO_ANT": 7.0,
                    "PLIEGUE_MEDIAL_PIERNA": 9.0,
                    "DIAMETRO_BIEPI_MUNECA": 55.0,
                    "DIAMETRO_BIEPI_FEMUR": 88.0,
                    "DIAMETRO_CODO": 66.0,
                    "CIRCUNFERENCIA_CARPO": 20.5,
                    "PERIMETRO_BICED_CONTRAIDO": 34.2,
                    "PERIMETRO_PIERNA": 52.0,
                }
            ],
        }

    def tearDown(self):
        valoracion_module.ApiClient = self.original_api_client
        valoracion_module.show_dashboard = self.original_show_dashboard

    def _select_athlete(self):
        search = find_text_field(self.view, "Buscar Deportista (ID o Nombre) *")
        search.value = "1001"
        search.suffix.on_click(None)

    def test_search_athlete_uses_api_and_displays_selected_data(self):
        self._select_athlete()
        self.assertEqual(FakeApiClient.calls[0][0], "list_deportistas")
        self.assertEqual(FakeApiClient.calls[0][1], "1001")
        visible_texts = [
            control.value
            for control in walk_controls(self.view)
            if isinstance(control, ft.Text) and isinstance(control.value, str)
        ]
        self.assertIn("Estudiante 1", visible_texts)
        self.assertIn("1001", visible_texts)
        self.assertIn("Pereira", visible_texts)

    def test_search_athlete_calculates_age_before_birthday(self):
        FakeApiClient.athletes[0]["FECHA_NAC"] = "2007-12-31"
        fecha_field = find_text_field(self.view, "Fecha Medición *")
        fecha_field.value = "2026-12-01"

        self._select_athlete()

        visible_texts = [
            control.value
            for control in walk_controls(self.view)
            if isinstance(control, ft.Text) and isinstance(control.value, str)
        ]
        self.assertTrue(any(text.startswith("18 ") for text in visible_texts))

    def test_search_athlete_shows_stored_valuations(self):
        FakeApiClient.editable_records = [self.stored_record()]
        self._select_athlete()
        self.assertIn(("list_somatotipos_editables", "1001"), FakeApiClient.calls)
        texts = [
            control.value
            for control in walk_controls(self.view)
            if isinstance(control, ft.Text) and isinstance(control.value, str)
        ]
        self.assertIn("ID 10 | Fecha: 2026-06-08", texts)
        self.assertIn("1 medicion(es) editable(s)", texts)

    def test_delete_stored_valuation_uses_delete_endpoint(self):
        FakeApiClient.editable_records = [self.stored_record()]
        self._select_athlete()
        find_button(self.view, "Eliminar").on_click(None)
        self.assertEqual(FakeApiClient.deleted_ids, [10])

    def test_load_stored_valuation_calls_api(self):
        record = self.stored_record()
        FakeApiClient.editable_records = [record]
        FakeApiClient.loaded_records = {10: record}
        self._select_athlete()
        find_button(self.view, "Cargar").on_click(None)
        self.assertIn(("get_somatotipo_editable", 10), FakeApiClient.calls)

    def test_view_initializes_with_date(self):
        fecha_field = find_text_field(self.view, "Fecha Medición *")
        self.assertTrue(fecha_field.value)

    def test_view_has_wizard_steps(self):
        texts = [
            control.value
            for control in walk_controls(self.view)
            if isinstance(control, ft.Text) and isinstance(control.value, str)
        ]
        self.assertIn("Datos Básicos", texts)


if __name__ == "__main__":
    unittest.main()
