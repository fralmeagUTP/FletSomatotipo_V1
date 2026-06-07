import tempfile
import unittest
from datetime import date, timedelta
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.backend.auth_utils import create_access_token, decode_token, get_current_user
from src.backend.main import app
from src.backend.schemas.deportistas import DeportistaCreate
from src.backend.schemas.somatotipo import SomatotipoCreate, SomatotipoDetalleBase


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_public_root_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Somatotipo API is running")

    def test_private_route_requires_token(self):
        response = self.client.get("/deportistas/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def test_access_token_decodes_subject(self):
        token = create_access_token({"sub": "tester", "id": 1})
        payload = decode_token(token)

        self.assertEqual(payload["sub"], "tester")
        self.assertEqual(payload["id"], 1)


class ValidationTests(unittest.TestCase):
    def test_invalid_athlete_is_rejected(self):
        with self.assertRaises(ValidationError):
            DeportistaCreate(
                IDENTI_DEPORTISTA="",
                TIPO_IDENTI=0,
                NOMBRE_DEPORTISTA="",
                SEXO_DEPORTISTA="X",
                E_MAIL="correo-invalido",
            )

    def test_valid_athlete_normalizes_sex(self):
        athlete = DeportistaCreate(
            IDENTI_DEPORTISTA="123",
            TIPO_IDENTI=1,
            NOMBRE_DEPORTISTA="Atleta Prueba",
            SEXO_DEPORTISTA="f",
            E_MAIL="atleta@example.com",
        )

        self.assertEqual(athlete.SEXO_DEPORTISTA, "F")

    def test_empty_email_is_normalized(self):
        athlete = DeportistaCreate(
            IDENTI_DEPORTISTA="123",
            TIPO_IDENTI=1,
            NOMBRE_DEPORTISTA="Atleta Prueba",
            SEXO_DEPORTISTA="M",
            E_MAIL="",
        )

        self.assertIsNone(athlete.E_MAIL)

    def test_invalid_measurement_is_rejected(self):
        with self.assertRaises(ValidationError):
            SomatotipoDetalleBase(
                ESTA_USER_CM=0,
                PESO_kg=0,
                PLIEGUE_TRICIPITAL=0,
                PLIEGUE_SUBESCAPULAR=0,
                PLIEGUE_SUPRAILIACO=0,
                PLIEGUE_ABDOMINAL=0,
                PLIEGUE_MUSLO_ANT=0,
                PLIEGUE_MEDIAL_PIERNA=0,
                DIAMETRO_BIEPI_MUNECA=0,
                DIAMETRO_BIEPI_FEMUR=0,
                DIAMETRO_CODO=0,
                PERIMETRO_BICED_CONTRAIDO=0,
                PERIMETRO_PIERNA=0,
                CIRCUNFERENCIA_CARPO=0,
            )

    def test_future_measure_date_is_rejected(self):
        detail = SomatotipoDetalleBase(
            ESTA_USER_CM=170,
            PESO_kg=70,
            PLIEGUE_TRICIPITAL=10,
            PLIEGUE_SUBESCAPULAR=10,
            PLIEGUE_SUPRAILIACO=10,
            PLIEGUE_ABDOMINAL=10,
            PLIEGUE_MUSLO_ANT=10,
            PLIEGUE_MEDIAL_PIERNA=10,
            DIAMETRO_BIEPI_MUNECA=50,
            DIAMETRO_BIEPI_FEMUR=80,
            DIAMETRO_CODO=50,
            PERIMETRO_BICED_CONTRAIDO=30,
            PERIMETRO_PIERNA=40,
            CIRCUNFERENCIA_CARPO=18,
        )

        with self.assertRaises(ValidationError):
            SomatotipoCreate(
                IDENTI_DEPORTISTA="123",
                LOGIN_USER="tester",
                FECHA_MEDIDA=date.today() + timedelta(days=1),
                DETALLES=[detail],
            )


class UploadTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: object()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_upload_rejects_non_image_extension(self):
        response = self.client.post(
            "/files/upload",
            files={"file": ("archivo.txt", BytesIO(b"texto"), "text/plain")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("JPG o PNG", response.json()["detail"])

    def test_upload_accepts_png(self):
        with tempfile.TemporaryDirectory() as upload_dir:
            with patch("src.backend.routers.files.UPLOAD_DIR", upload_dir):
                response = self.client.post(
                    "/files/upload",
                    files={"file": ("foto.png", BytesIO(b"png"), "image/png")},
                )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["url"].endswith(".png"))


if __name__ == "__main__":
    unittest.main()
