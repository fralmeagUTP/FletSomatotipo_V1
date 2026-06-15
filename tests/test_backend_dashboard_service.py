import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from src.backend.models import Deporte, DeporteDeportista, Deportista, Entidad, Somatotipo
from src.backend.services.dashboard_service import get_dashboard_summary


class FakeQuery:
    def __init__(self, total, items=None):
        self.total = total
        self.items = items or []

    def count(self):
        return self.total

    def order_by(self, *_args):
        return self

    def limit(self, _limit):
        return self

    def all(self):
        return self.items


class FakeDb:
    recent = [
        SimpleNamespace(
            id_Somatotipo=12,
            FECHA_MEDIDA=date(2026, 6, 10),
            IDENTI_DEPORTISTA="1001",
            deportista=SimpleNamespace(NOMBRE_DEPORTISTA="Estudiante 1"),
        )
    ]

    def query(self, model):
        if model is Deportista:
            return FakeQuery(7)
        if model is Somatotipo:
            return FakeQuery(3, self.recent)
        if model is Deporte:
            return FakeQuery(4)
        if model is Entidad:
            return FakeQuery(2)
        if model is DeporteDeportista:
            return FakeQuery(5)
        raise AssertionError(f"Modelo no esperado: {model}")


class DashboardServiceTests(unittest.TestCase):
    def test_get_dashboard_summary_counts_records_and_contract(self):
        contract = {"ok": True, "missing": []}

        with patch(
            "src.backend.services.dashboard_service.get_somatotipo_view_contract",
            return_value=contract,
        ):
            result = get_dashboard_summary(FakeDb())

        self.assertEqual(result["total_deportistas"], 7)
        self.assertEqual(result["total_valoraciones"], 3)
        self.assertEqual(result["total_deportes"], 4)
        self.assertEqual(result["total_entidades"], 2)
        self.assertEqual(result["total_asignaciones"], 5)
        self.assertEqual(
            result["actividad_reciente"],
            [
                {
                    "id_Somatotipo": 12,
                    "fecha": "2026-06-10",
                    "deportista_id": "1001",
                    "deportista": "Estudiante 1",
                }
            ],
        )
        self.assertEqual(result["vista_contrato"], contract)


if __name__ == "__main__":
    unittest.main()
