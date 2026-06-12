import unittest
from unittest.mock import patch

from src.backend.models import Deportista, Somatotipo
from src.backend.services.dashboard_service import get_dashboard_summary


class FakeQuery:
    def __init__(self, total):
        self.total = total

    def count(self):
        return self.total


class FakeDb:
    def query(self, model):
        if model is Deportista:
            return FakeQuery(7)
        if model is Somatotipo:
            return FakeQuery(3)
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
        self.assertEqual(result["vista_contrato"], contract)


if __name__ == "__main__":
    unittest.main()
