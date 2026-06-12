import unittest

from src.backend.services.view_contract_service import (
    EXPECTED_SOMATOTIPO_VIEW_COLUMNS,
    SOMATOTIPO_VIEW_NAME,
    evaluate_contract,
)


class ViewContractTests(unittest.TestCase):
    def test_evaluate_contract_accepts_expected_columns(self):
        result = evaluate_contract(EXPECTED_SOMATOTIPO_VIEW_COLUMNS)

        self.assertTrue(result["ok"])
        self.assertEqual(result["view"], SOMATOTIPO_VIEW_NAME)
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["extra"], [])

    def test_evaluate_contract_reports_missing_and_extra_columns(self):
        result = evaluate_contract(["id_Somatotipo", "COLUMNA_EXTRA"])

        self.assertFalse(result["ok"])
        self.assertIn("FECHA_MEDIDA", result["missing"])
        self.assertEqual(result["extra"], ["COLUMNA_EXTRA"])


if __name__ == "__main__":
    unittest.main()
