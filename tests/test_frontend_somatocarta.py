import unittest

import flet as ft

from src.frontend.assets import REFERENCE_IMAGES
from src.frontend.somatocarta import CHART_HEIGHT, CHART_WIDTH, build_somatocarta_card, build_somatocarta_chart, coordinate_to_pixel, parse_coordinate


class SomatocartaTests(unittest.TestCase):
    def test_parse_coordinate_accepts_decimal_comma(self):
        self.assertEqual(parse_coordinate("1,25"), 1.25)

    def test_coordinate_to_pixel_maps_origin_to_center_axes(self):
        x_position, y_position = coordinate_to_pixel(0, 0)

        self.assertAlmostEqual(x_position, 368.15)
        self.assertAlmostEqual(y_position, 593.71)

    def test_coordinate_to_pixel_places_reported_athlete_coordinates_on_axes(self):
        x_position, y_position = coordinate_to_pixel(-0.28, 9.15)

        self.assertAlmostEqual(x_position, 358.09)
        self.assertAlmostEqual(y_position, 389.66)

    def test_coordinate_to_pixel_keeps_capture_sequence_on_visible_ticks(self):
        positions = [
            coordinate_to_pixel(-0.28, 9.15),
            coordinate_to_pixel(-0.47, 8.93),
            coordinate_to_pixel(-0.65, 8.67),
            coordinate_to_pixel(-0.84, 8.40),
            coordinate_to_pixel(-1.02, 8.19),
        ]

        for previous_position, current_position in zip(positions, positions[1:]):
            self.assertLess(current_position[0], previous_position[0])
            self.assertGreater(current_position[1], previous_position[1])

    def test_build_somatocarta_chart_uses_reference_image_and_plots_athlete(self):
        chart = build_somatocarta_chart("2.5", "-1.5", "Estudiante 1")

        self.assertIsInstance(chart, ft.Stack)
        self.assertEqual(chart.width, CHART_WIDTH)
        self.assertEqual(chart.height, CHART_HEIGHT)
        self.assertIsInstance(chart.controls[0], ft.Image)
        self.assertIn(REFERENCE_IMAGES["somatocarta"], chart.controls[0].src)
        labels = [
            control.content.value
            for control in chart.controls
            if isinstance(control, ft.Container) and isinstance(getattr(control, "content", None), ft.Text)
        ]
        self.assertIn("Estudiante 1", labels)

    def test_build_somatocarta_card_shows_empty_state_without_coordinates(self):
        card = build_somatocarta_card(None, None, "Ana")

        self.assertIn("Somatocarta", card.content.controls[0].value)
        self.assertIn("sin coordenadas", card.content.controls[1].value)
        self.assertIsInstance(card.content.controls[2], ft.Text)


if __name__ == "__main__":
    unittest.main()
