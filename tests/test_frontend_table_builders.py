import unittest

from src.frontend.table_builders import (
    build_deportista_row,
    build_historial_item,
    build_measurement_row,
    group_historial_rows,
)


class TableBuildersTests(unittest.TestCase):
    def test_group_historial_rows_groups_details_by_somatotipo_id(self):
        rows = [
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "NOMBRE_DEPORTISTA": "Ana", "EDAD": 20},
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "NOMBRE_DEPORTISTA": "Ana", "EDAD": 20},
            {"id_Somatotipo": 2, "FECHA_MEDIDA": "2026-06-02", "NOMBRE_DEPORTISTA": "Luis", "EDAD": 22},
        ]

        grouped = group_historial_rows(rows)

        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped[1]["detalles"]), 2)
        self.assertEqual(grouped[2]["NOMBRE_DEPORTISTA"], "Luis")

    def test_build_deportista_row_contains_visible_values(self):
        row = build_deportista_row(
            {
                "IDENTI_DEPORTISTA": "123",
                "NOMBRE_DEPORTISTA": "Ana",
                "SEXO_DEPORTISTA": "F",
                "FECHA_NAC": "2000-01-01",
                "CIUDAD_RESI": "Medellín",
                "E_MAIL": "",
                "TELEFONO": "300",
            },
            on_edit=lambda item: None,
            on_delete=lambda item_id: None,
        )

        self.assertEqual(row.cells[0].content.value, "123")
        self.assertEqual(row.cells[1].content.value, "Ana")
        self.assertEqual(row.cells[5].content.value, "300")

    def test_build_historial_item_shows_measurement_summary(self):
        item = {
            "FECHA_MEDIDA": "2026-06-01",
            "NOMBRE_DEPORTISTA": "Ana",
            "PESO_kg": 65,
            "IMC": 22.5,
            "PorcRasoYuasz": 15,
        }

        card = build_historial_item(10, item, on_select=lambda selected: None, on_delete=lambda item_id: None)
        summary = card.content.controls[2].value

        self.assertIn("ID: 10", summary)
        self.assertIn("Peso: 65 kg", summary)

    def test_build_measurement_row_contains_summary_values(self):
        row = build_measurement_row(
            {
                "PESO_kg": 75,
                "ESTA_USER_CM": 180,
                "PLIEGUE_TRICIPITAL": 10,
                "PLIEGUE_SUBESCAPULAR": 11,
            },
            on_delete=lambda item: None,
        )

        self.assertEqual(row.cells[1].content.value, "75")
        self.assertEqual(row.cells[2].content.value, "180")
        self.assertIn("Tri:10", row.cells[3].content.value)

    def test_build_measurement_row_can_include_edit_action(self):
        row = build_measurement_row(
            {
                "PESO_kg": 75,
                "ESTA_USER_CM": 180,
                "PLIEGUE_TRICIPITAL": 10,
                "PLIEGUE_SUBESCAPULAR": 11,
            },
            on_delete=lambda item: None,
            on_edit=lambda item: None,
        )

        actions = row.cells[4].content.controls

        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].tooltip, "Editar medición")
        self.assertEqual(actions[1].tooltip, "Eliminar medición")

    def test_build_measurement_row_shows_take_index(self):
        row = build_measurement_row(
            {
                "PESO_kg": 75,
                "ESTA_USER_CM": 180,
                "PLIEGUE_TRICIPITAL": 10,
                "PLIEGUE_SUBESCAPULAR": 11,
            },
            on_delete=lambda item: None,
            index=2,
        )

        self.assertEqual(row.cells[0].content.value, "#2")


if __name__ == "__main__":
    unittest.main()
