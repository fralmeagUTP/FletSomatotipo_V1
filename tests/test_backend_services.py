import unittest
from types import SimpleNamespace

from src.backend.services.deportistas_service import create_deportista, list_deportistas_page
from src.backend.services.somatotipo_service import create_somatotipo, get_historial_vista_page


class FakeDetail:
    def model_dump(self):
        return {
            "ESTA_USER_CM": 180,
            "PESO_kg": 75,
            "PLIEGUE_TRICIPITAL": 10,
            "PLIEGUE_SUBESCAPULAR": 11,
            "PLIEGUE_SUPRAILIACO": 12,
            "PLIEGUE_ABDOMINAL": 13,
            "PLIEGUE_MUSLO_ANT": 14,
            "PLIEGUE_MEDIAL_PIERNA": 15,
            "DIAMETRO_BIEPI_MUNECA": 6,
            "DIAMETRO_BIEPI_FEMUR": 9,
            "DIAMETRO_CODO": 7,
            "PERIMETRO_BICED_CONTRAIDO": 32,
            "PERIMETRO_PIERNA": 40,
            "CIRCUNFERENCIA_CARPO": 17,
        }


class FakeDb:
    def __init__(self, fail_on_commit=False, fail_on_flush=False):
        self.added = []
        self.commits = 0
        self.flushes = 0
        self.rollbacks = 0
        self.refreshed = []
        self.fail_on_commit = fail_on_commit
        self.fail_on_flush = fail_on_flush

    def add(self, item):
        self.added.append(item)

    def flush(self):
        if self.fail_on_flush:
            raise RuntimeError("flush failed")
        self.flushes += 1
        self.added[0].id_Somatotipo = 99

    def commit(self):
        if self.fail_on_commit:
            raise RuntimeError("commit failed")
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def refresh(self, item):
        self.refreshed.append(item)

    def query(self, model):
        return FakeQuery()


class FakeQuery:
    def __init__(self):
        self.offset_value = None
        self.limit_value = None

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return None

    def count(self):
        return 36

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return ["item"]


class BackendServicesTests(unittest.TestCase):
    def test_list_deportistas_page_applies_offset_and_limit(self):
        db = FakeDb()

        result = list_deportistas_page(db, page=3, page_size=10)

        self.assertEqual(result["items"], ["item"])
        self.assertEqual(result["total"], 36)
        self.assertEqual(result["page"], 3)
        self.assertEqual(result["page_size"], 10)

    def test_get_historial_vista_page_applies_offset_and_limit(self):
        db = FakeDb()

        result = get_historial_vista_page(db, "123", page=2, page_size=5)

        self.assertEqual(result["items"], ["item"])
        self.assertEqual(result["total"], 36)
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["page_size"], 5)

    def test_create_somatotipo_flushes_header_and_commits_once(self):
        db = FakeDb()
        payload = SimpleNamespace(
            IDENTI_DEPORTISTA="123",
            LOGIN_USER="admin",
            FECHA_MEDIDA="2026-06-06",
            OBSERV="Obs",
            DETALLES=[FakeDetail()],
        )

        result = create_somatotipo(db, payload)

        self.assertEqual(result["id"], 99)
        self.assertEqual(db.flushes, 1)
        self.assertEqual(db.commits, 1)
        self.assertEqual(len(db.added), 2)
        self.assertEqual(db.added[1].id_Somatotipo, 99)

    def test_create_somatotipo_rolls_back_on_flush_failure(self):
        db = FakeDb(fail_on_flush=True)
        payload = SimpleNamespace(
            IDENTI_DEPORTISTA="123",
            LOGIN_USER="admin",
            FECHA_MEDIDA="2026-06-06",
            OBSERV="Obs",
            DETALLES=[FakeDetail()],
        )

        with self.assertRaises(RuntimeError):
            create_somatotipo(db, payload)

        self.assertEqual(db.rollbacks, 1)

    def test_create_deportista_rolls_back_on_commit_failure(self):
        db = FakeDb(fail_on_commit=True)
        payload = {
            "IDENTI_DEPORTISTA": "123",
            "TIPO_IDENTI": 1,
            "NOMBRE_DEPORTISTA": "Ana",
            "SEXO_DEPORTISTA": "F",
        }

        with self.assertRaises(RuntimeError):
            create_deportista(db, payload)

        self.assertEqual(db.rollbacks, 1)


if __name__ == "__main__":
    unittest.main()
