import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from src.backend.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_token, get_current_user
from src.backend.database import get_db
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

    def test_login_reports_database_unavailable(self):
        class UnavailableSession:
            def query(self, *_):
                raise OperationalError("SELECT", {}, Exception("database unavailable"))

            def rollback(self):
                pass

        app.dependency_overrides[get_db] = lambda: UnavailableSession()

        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "secret"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("base de datos", response.json()["detail"])

    def test_access_token_decodes_subject(self):
        token = create_access_token({"sub": "tester", "id": 1})
        payload = decode_token(token)

        self.assertEqual(payload["sub"], "tester")
        self.assertEqual(payload["id"], 1)

    def test_access_token_uses_configured_expiration(self):
        token = create_access_token({"sub": "tester", "id": 1})
        payload = decode_token(token)
        remaining_seconds = payload["exp"] - int(datetime.now(timezone.utc).timestamp())

        self.assertGreaterEqual(remaining_seconds, ACCESS_TOKEN_EXPIRE_MINUTES * 60 - 5)
        self.assertLessEqual(remaining_seconds, ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 5)


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


class PdfDownloadTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: object()
        app.dependency_overrides[get_db] = lambda: object()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_download_valoracion_pdf_returns_attachment(self):
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.build_valoracion_pdf_response",
            return_value=b"%PDF-1.4 prueba",
        ):
            response = self.client.get("/somatotipo/99/pdf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("valoracion_99.pdf", response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))

    def test_download_longitudinal_pdf_returns_attachment(self):
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.build_longitudinal_pdf_response",
            return_value=b"%PDF-1.4 longitudinal",
        ) as builder:
            response = self.client.get("/somatotipo/vista/deportista/123/longitudinal/pdf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("analisis_longitudinal_123.pdf", response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))
        builder.assert_called_once()


class SomatotipoEditableRouteTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: object()
        app.dependency_overrides[get_db] = lambda: object()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_list_editable_somatotipos_returns_service_payload(self):
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.list_somatotipos_editables",
            return_value=[{"id_Somatotipo": 1, "DETALLES": [{"ID": 2}]}],
        ) as service:
            response = self.client.get("/somatotipo/editable/deportista/123")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["DETALLES"][0]["ID"], 2)
        service.assert_called_once()

    def test_get_editable_somatotipo_returns_service_payload(self):
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.get_somatotipo_editable_or_404",
            return_value={"id_Somatotipo": 99, "DETALLES": []},
        ) as service:
            response = self.client.get("/somatotipo/editable/99")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id_Somatotipo"], 99)
        service.assert_called_once()

    def test_update_somatotipo_detail_returns_updated_detail(self):
        payload = {
            "ESTA_USER_CM": 170,
            "PESO_kg": 70,
            "PLIEGUE_TRICIPITAL": 10,
            "PLIEGUE_SUBESCAPULAR": 10,
            "PLIEGUE_SUPRAILIACO": 10,
            "PLIEGUE_ABDOMINAL": 10,
            "PLIEGUE_MUSLO_ANT": 10,
            "PLIEGUE_MEDIAL_PIERNA": 10,
            "DIAMETRO_BIEPI_MUNECA": 50,
            "DIAMETRO_BIEPI_FEMUR": 80,
            "DIAMETRO_CODO": 50,
            "PERIMETRO_BICED_CONTRAIDO": 30,
            "PERIMETRO_PIERNA": 40,
            "CIRCUNFERENCIA_CARPO": 18,
        }
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.update_somatotipo_detalle",
            return_value={"ID": 7, "PESO_kg": 70},
        ) as service:
            response = self.client.put("/somatotipo/detalle/7", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ID"], 7)
        service.assert_called_once()

    def test_create_somatotipo_detail_returns_created_detail(self):
        payload = {
            "ESTA_USER_CM": 170,
            "PESO_kg": 70,
            "PLIEGUE_TRICIPITAL": 10,
            "PLIEGUE_SUBESCAPULAR": 10,
            "PLIEGUE_SUPRAILIACO": 10,
            "PLIEGUE_ABDOMINAL": 10,
            "PLIEGUE_MUSLO_ANT": 10,
            "PLIEGUE_MEDIAL_PIERNA": 10,
            "DIAMETRO_BIEPI_MUNECA": 50,
            "DIAMETRO_BIEPI_FEMUR": 80,
            "DIAMETRO_CODO": 50,
            "PERIMETRO_BICED_CONTRAIDO": 30,
            "PERIMETRO_PIERNA": 40,
            "CIRCUNFERENCIA_CARPO": 18,
        }
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.create_somatotipo_detalle",
            return_value={"ID": 8, "id_Somatotipo": 99},
        ) as service:
            response = self.client.post("/somatotipo/99/detalle", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ID"], 8)
        service.assert_called_once()

    def test_delete_somatotipo_detail_returns_deleted_detail_id(self):
        with patch(
            "src.backend.routers.somatotipo.somatotipo_service.delete_somatotipo_detalle",
            return_value={"ID": 8, "message": "ok"},
        ) as service:
            response = self.client.delete("/somatotipo/detalle/8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ID"], 8)
        service.assert_called_once()


class EntidadesDeportesRouteTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: object()
        app.dependency_overrides[get_db] = lambda: object()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_entidades_crud_routes_delegate_to_service(self):
        payload = {"NIT_ENTIDAD": "900", "RAZON_SOCIAL": "Club", "E_MAIL": "club@example.com"}
        with patch(
            "src.backend.routers.entidades_deportes.entidades_deportes_service.list_entidades_page",
            return_value={"items": [], "total": 0, "page": 1, "page_size": 50},
        ) as list_service:
            response = self.client.get("/entidades/")
        self.assertEqual(response.status_code, 200)
        list_service.assert_called_once()

        with patch(
            "src.backend.routers.entidades_deportes.entidades_deportes_service.create_entidad",
            return_value=payload,
        ) as create_service:
            response = self.client.post("/entidades/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["NIT_ENTIDAD"], "900")
        create_service.assert_called_once()

    def test_deportes_crud_routes_delegate_to_service(self):
        payload = {"ID_DEPORTE": 7, "DEPORTE": "Natación"}
        with patch(
            "src.backend.routers.entidades_deportes.entidades_deportes_service.create_deporte",
            return_value=payload,
        ) as create_service:
            response = self.client.post("/deportes/", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ID_DEPORTE"], 7)
        create_service.assert_called_once()

    def test_asignaciones_crud_routes_delegate_to_service(self):
        payload = {"ID_DEPORTE": 7, "IDENTI_DEPORTISTA": "123", "NIT_ENTIDAD": "900"}
        response_payload = {"id": 1, **payload}
        with patch(
            "src.backend.routers.entidades_deportes.entidades_deportes_service.create_asignacion",
            return_value=response_payload,
        ) as create_service:
            response = self.client.post("/asignaciones/", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)
        create_service.assert_called_once()

        with patch(
            "src.backend.routers.entidades_deportes.entidades_deportes_service.delete_asignacion",
            return_value={"message": "ok"},
        ) as delete_service:
            response = self.client.delete("/asignaciones/1")

        self.assertEqual(response.status_code, 200)
        delete_service.assert_called_once()


if __name__ == "__main__":
    unittest.main()
