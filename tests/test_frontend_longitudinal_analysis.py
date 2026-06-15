import unittest

import flet as ft

from src.frontend.longitudinal_analysis import (
    LONGITUDINAL_METRICS,
    build_longitudinal_chart,
    build_longitudinal_somatocarta,
    build_metric_series,
    build_selected_metric_cards,
    build_somatocarta_points,
    compact_date_label,
    delta_text,
    percent_change_text,
    period_summary,
    parse_number,
    trend_summary,
)


class LongitudinalAnalysisTests(unittest.TestCase):
    def test_parse_number_accepts_decimal_comma(self):
        self.assertEqual(parse_number("22,75"), 22.75)

    def test_build_metric_series_sorts_by_date_and_skips_invalid_values(self):
        rows = [
            {"id_Somatotipo": 2, "FECHA_MEDIDA": "2026-06-02", "PESO_kg": "74"},
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "PESO_kg": "73"},
            {"id_Somatotipo": 3, "FECHA_MEDIDA": "2026-06-03", "PESO_kg": None},
        ]

        series = build_metric_series(rows, "PESO_kg")

        self.assertEqual([point["value"] for point in series], [73.0, 74.0])
        self.assertEqual([point["date"] for point in series], ["2026-06-01", "2026-06-02"])

    def test_trend_summary_reports_direction_and_unit(self):
        series = [
            {"value": 73.0, "date": "2026-06-01"},
            {"value": 75.5, "date": "2026-06-02"},
        ]

        self.assertIn("2 valoraciones", trend_summary(series, "kg"))
        self.assertIn("subió 2.50 kg", trend_summary(series, "kg"))

    def test_period_summary_reports_same_day_measurements(self):
        rows = [
            {"FECHA_MEDIDA": "2026-06-01", "id_Somatotipo": 1},
            {"FECHA_MEDIDA": "2026-06-01", "id_Somatotipo": 2},
        ]

        self.assertIn("registradas el 2026-06-01", period_summary(rows))

    def test_delta_text_formats_signed_change(self):
        series = [{"value": 73.0}, {"value": 75.5}]

        self.assertEqual(delta_text(series, "kg"), "+2.50 kg")

    def test_percent_change_text_formats_relative_change(self):
        series = [{"value": 100.0}, {"value": 90.0}]

        self.assertEqual(percent_change_text(series), "-10.00 %")

    def test_build_selected_metric_cards_has_four_summary_cards(self):
        series = [{"value": 73.0}, {"value": 75.5}]
        cards = build_selected_metric_cards(series, LONGITUDINAL_METRICS[0])

        self.assertEqual(len(cards.controls), 4)

    def test_compact_date_label_keeps_month_and_day(self):
        self.assertEqual(compact_date_label("2026-06-07"), "06-07")

    def test_build_longitudinal_chart_returns_line_chart_container(self):
        rows = [
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "PESO_kg": "73"},
            {"id_Somatotipo": 2, "FECHA_MEDIDA": "2026-06-02", "PESO_kg": "74"},
        ]

        container = build_longitudinal_chart(rows, LONGITUDINAL_METRICS[0])

        self.assertIsInstance(container.content, ft.Row)
        self.assertIsInstance(container.content.controls[0], ft.LineChart)
        self.assertEqual(len(container.content.controls[0].bottom_axis.labels), 2)

    def test_build_somatocarta_points_sorts_dates_and_skips_missing_coordinates(self):
        rows = [
            {"id_Somatotipo": 3, "FECHA_MEDIDA": "2026-06-03", "X": None, "Y": "8.0"},
            {"id_Somatotipo": 2, "FECHA_MEDIDA": "2026-06-02", "X": "-0.47", "Y": "8.93"},
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "X": "-0.28", "Y": "9.15"},
        ]

        points = build_somatocarta_points(rows)

        self.assertEqual([point["date"] for point in points], ["2026-06-01", "2026-06-02"])
        self.assertEqual([point["x"] for point in points], [-0.28, -0.47])

    def test_build_longitudinal_somatocarta_shows_all_dates_and_coordinate_legend(self):
        rows = [
            {"id_Somatotipo": 1, "FECHA_MEDIDA": "2026-06-01", "X": "-0.28", "Y": "9.15"},
            {"id_Somatotipo": 2, "FECHA_MEDIDA": "2026-06-02", "X": "-0.47", "Y": "8.93"},
        ]

        card = build_longitudinal_somatocarta(rows)
        stack = card.content.controls[2].controls[0]
        legend = card.content.controls[3].content

        self.assertIsInstance(stack, ft.Stack)
        self.assertEqual(len(stack.controls), 4)
        self.assertIn("X=-0.28", legend.controls[0].content.controls[1].value)


if __name__ == "__main__":
    unittest.main()
