import unittest

import flet as ft

from src.frontend.composition_analysis import (
    build_composition_panel,
    build_composition_rows,
    build_composition_table,
    build_fat_method_rows,
    build_fat_methods_table,
    build_mass_distribution_rows,
    build_mass_distribution_table,
    build_mass_pie_chart,
    mass_balance_message,
    mass_balance_summary,
)


class CompositionAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.detail = {
            "PESO_kg": 55.5,
            "PorcRasoYuasz": 15.81,
            "PorcGrasoFaulker": 14.2,
            "PorcGrasoJonson": 13.9,
            "PesoRasoYuazs": 8.77,
            "PesoRasoFaulker": 7.88,
            "PesoGrasoJhonston": 7.71,
            "Mma": 28.38,
            "PesoOseo": 9.24,
            "PesoResidual": 13.38,
        }

    def test_build_composition_rows_integrates_percent_mass_unit_and_method(self):
        rows = build_composition_rows(self.detail)

        self.assertEqual(rows[0]["component"], "Grasa corporal")
        self.assertEqual(rows[0]["unit"], "%")
        self.assertEqual(rows[0]["method"], "Johnston")
        self.assertEqual(rows[3]["component"], "Masa grasa")
        self.assertEqual(rows[3]["unit"], "kg")
        self.assertEqual(rows[2]["method"], "Yuhasz")
        self.assertEqual(rows[3]["method"], "Johnston")

    def test_mass_balance_summary_uses_johnston_mass_and_detects_difference(self):
        summary = mass_balance_summary(self.detail)

        self.assertTrue(summary["is_warning"])
        self.assertAlmostEqual(summary["component_total"], 58.71)
        self.assertIn("Masa grasa Johnston", mass_balance_message(summary))
        self.assertIn("diferencia significativa", mass_balance_message(summary))

    def test_mass_balance_summary_accepts_coherent_components(self):
        detail = dict(self.detail, PesoResidual=10.17)
        summary = mass_balance_summary(detail)

        self.assertFalse(summary["is_warning"])
        self.assertIn("coherente", mass_balance_message(summary))

    def test_build_mass_distribution_rows_reports_kg_and_percent(self):
        rows = build_mass_distribution_rows(self.detail)

        self.assertEqual(rows[0]["component"], "Peso corporal")
        self.assertEqual(rows[1]["component"], "Masa grasa Johnston")
        self.assertAlmostEqual(rows[1]["value"], 7.71)
        self.assertAlmostEqual(rows[1]["percent"], 13.891891891891891)
        self.assertEqual(rows[-2]["component"], "Suma calculada")
        self.assertAlmostEqual(rows[-2]["value"], 58.71)

    def test_build_fat_method_rows_groups_percent_and_mass_by_method(self):
        rows = build_fat_method_rows(self.detail)

        self.assertEqual([row["method"] for row in rows], ["Johnston", "Faulkner", "Yuhasz"])
        self.assertEqual(rows[0]["use"], "Método principal")
        self.assertAlmostEqual(rows[0]["fat_percent"], 13.9)
        self.assertAlmostEqual(rows[0]["fat_mass"], 7.71)

    def test_build_composition_table_returns_horizontal_scroll_row(self):
        table = build_composition_table(build_composition_rows(self.detail))

        self.assertIsInstance(table, ft.Row)
        self.assertEqual(table.scroll, ft.ScrollMode.AUTO)

    def test_build_fat_methods_table_returns_horizontal_scroll_row(self):
        table = build_fat_methods_table(build_fat_method_rows(self.detail))

        self.assertIsInstance(table, ft.Row)
        self.assertEqual(table.scroll, ft.ScrollMode.AUTO)

    def test_build_mass_distribution_table_returns_horizontal_scroll_row(self):
        table = build_mass_distribution_table(build_mass_distribution_rows(self.detail))

        self.assertIsInstance(table, ft.Row)
        self.assertEqual(table.scroll, ft.ScrollMode.AUTO)

    def test_build_mass_pie_chart_returns_responsive_chart(self):
        chart = build_mass_pie_chart(build_mass_distribution_rows(self.detail))

        self.assertIsInstance(chart, ft.ResponsiveRow)
        self.assertIsInstance(chart.controls[0].content, ft.PieChart)

    def test_build_composition_panel_contains_integrated_sections(self):
        panel = build_composition_panel(self.detail)

        self.assertIsInstance(panel, ft.Column)
        self.assertGreaterEqual(len(panel.controls), 4)


if __name__ == "__main__":
    unittest.main()
