import unittest

from src.frontend.interpretation import (
    bmi_methodology_note,
    fat_equation_warning,
    longitudinal_reliability_message,
)


class InterpretationTests(unittest.TestCase):
    def test_bmi_note_warns_for_under_20_years(self):
        note = bmi_methodology_note(16, 21.68)

        self.assertIn("menores de 20 años", note)
        self.assertIn("edad y sexo", note)

    def test_fat_equation_warning_detects_large_difference(self):
        warning = fat_equation_warning(
            {
                "PorcRasoYuasz": 15.81,
                "PorcGrasoFaulker": 9.08,
            }
        )

        self.assertIn("Diferencia entre ecuaciones", warning)

    def test_longitudinal_reliability_message_for_two_measurements(self):
        self.assertIn("Comparación entre dos mediciones", longitudinal_reliability_message(2))


if __name__ == "__main__":
    unittest.main()
