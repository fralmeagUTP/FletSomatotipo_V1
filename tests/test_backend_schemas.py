import unittest
from datetime import date, timedelta

from pydantic import ValidationError

from src.backend.schemas.deportistas import DeportistaCreate
from src.backend.schemas.somatotipo import SomatotipoCreate


class BackendSchemasTests(unittest.TestCase):
    def test_deportista_schema_normalizes_empty_optional_email(self):
        payload = {
            "IDENTI_DEPORTISTA": " 123 ",
            "TIPO_IDENTI": 1,
            "NOMBRE_DEPORTISTA": " Ana ",
            "SEXO_DEPORTISTA": "f",
            "E_MAIL": "",
        }

        model = DeportistaCreate(**payload)

        self.assertEqual(model.IDENTI_DEPORTISTA, "123")
        self.assertEqual(model.NOMBRE_DEPORTISTA, "Ana")
        self.assertEqual(model.SEXO_DEPORTISTA, "F")
        self.assertIsNone(model.E_MAIL)

    def test_deportista_schema_rejects_future_birth_date(self):
        payload = {
            "IDENTI_DEPORTISTA": "123",
            "TIPO_IDENTI": 1,
            "NOMBRE_DEPORTISTA": "Ana",
            "SEXO_DEPORTISTA": "F",
            "FECHA_NAC": date.today() + timedelta(days=1),
        }

        with self.assertRaises(ValidationError):
            DeportistaCreate(**payload)

    def test_somatotipo_schema_requires_at_least_one_detail(self):
        payload = {
            "IDENTI_DEPORTISTA": "123",
            "LOGIN_USER": "admin",
            "FECHA_MEDIDA": date.today(),
            "DETALLES": [],
        }

        with self.assertRaises(ValidationError):
            SomatotipoCreate(**payload)

    def test_somatotipo_schema_rejects_out_of_range_measurements(self):
        detail = {
            "ESTA_USER_CM": 251,
            "PESO_kg": 75,
            "PLIEGUE_TRICIPITAL": 10,
            "PLIEGUE_SUBESCAPULAR": 11,
            "PLIEGUE_SUPRAILIACO": 12,
            "PLIEGUE_ABDOMINAL": 13,
            "PLIEGUE_MUSLO_ANT": 14,
            "PLIEGUE_MEDIAL_PIERNA": 15,
            "DIAMETRO_BIEPI_MUNECA": 60,
            "DIAMETRO_BIEPI_FEMUR": 90,
            "DIAMETRO_CODO": 70,
            "PERIMETRO_BICED_CONTRAIDO": 32,
            "PERIMETRO_PIERNA": 40,
            "CIRCUNFERENCIA_CARPO": 17,
        }
        payload = {
            "IDENTI_DEPORTISTA": "123",
            "LOGIN_USER": "admin",
            "FECHA_MEDIDA": date.today(),
            "DETALLES": [detail],
        }

        with self.assertRaises(ValidationError):
            SomatotipoCreate(**payload)


if __name__ == "__main__":
    unittest.main()
