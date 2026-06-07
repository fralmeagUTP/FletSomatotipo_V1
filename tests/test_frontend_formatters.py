import unittest
from datetime import date

from src.frontend.formatters import age_from_birth_date, display_value


class FormatterTests(unittest.TestCase):
    def test_display_value_handles_empty_values(self):
        self.assertEqual(display_value(None), "-")
        self.assertEqual(display_value(""), "-")
        self.assertEqual(display_value("  "), "-")
        self.assertEqual(display_value(" Pereira "), "Pereira")

    def test_age_from_birth_date_accepts_iso_string(self):
        self.assertEqual(age_from_birth_date("2000-06-06", date(2026, 6, 6)), "26")

    def test_age_from_birth_date_before_birthday(self):
        self.assertEqual(age_from_birth_date(date(2000, 12, 10), date(2026, 6, 6)), "25")

    def test_age_from_birth_date_rejects_invalid_value(self):
        self.assertEqual(age_from_birth_date("fecha-mala", date(2026, 6, 6)), "-")


if __name__ == "__main__":
    unittest.main()
