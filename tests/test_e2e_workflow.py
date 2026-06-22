import tempfile
import unittest
from datetime import date
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.database import Base, get_db
from src.backend.main import app
from src.backend.models import Usuario, VistaValoracionCorporal


MEASUREMENT = {
    "ESTA_USER_CM": 170,
    "PESO_kg": 65,
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


def valuation_view(valuation_id, measured_on, weight):
    return VistaValoracionCorporal(
        id_Somatotipo=valuation_id,
        FECHA_MEDIDA=measured_on,
        IDENTI_DEPORTISTA="E2E-001",
        NOMBRE_DEPORTISTA="Atleta E2E",
        SEXO_DEPORTISTA="F",
        EDAD=26,
        ESTA_USER_CM=170,
        PESO_kg=weight,
        PLIEGUE_TRICIPITAL=10,
        PLIEGUE_SUBESCAPULAR=11,
        PLIEGUE_SUPRAILIACO=12,
        PLIEGUE_ABDOMINAL=13,
        PLIEGUE_MUSLO_ANT=14,
        PLIEGUE_MEDIAL_PIERNA=15,
        DIAMETRO_BIEPI_MUNECA=60,
        DIAMETRO_BIEPI_FEMUR=90,
        DIAMETRO_CODO=70,
        PERIMETRO_BICED_CONTRAIDO=32,
        PERIMETRO_PIERNA=40,
        CIRCUNFERENCIA_CARPO=17,
        PorcRasoYuasz=18.2,
        PesoRasoYuazs=11.8,
        PorcGrasoFaulker=20.1,
        PesoRasoFaulker=13.1,
        PesoOseo=8.2,
        PesoResidual=13.6,
        Mma=31.4,
        IMC=22.5,
        EstadoIMC="Normal",
        Complexion=10,
        TipoComplexion="Media",
        Endomorfismo=3.1,
        EscalaEndomorfismo="Moderado",
        Mesomorfismo=4.2,
        EscalaMesomorfismo="Alto",
        Ectomorfismo=2.0,
        EscalaEctomorfismo="Bajo",
        X=-1.1,
        Y=3.3,
    )


class CriticalWorkflowE2ETests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        with self.SessionLocal() as database:
            database.add(
                Usuario(
                    LOGIN_USER="e2e",
                    PSW_USER="e2e-secret",
                    NOM_USER="Evaluador E2E",
                )
            )
            database.commit()

        def override_database():
            database = self.SessionLocal()
            try:
                yield database
            finally:
                database.close()

        app.dependency_overrides[get_db] = override_database
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_authenticated_workflow_reaches_pdf_and_cleans_dependencies(self):
        login = self.client.post("/auth/login", json={"username": "e2e", "password": "e2e-secret"})
        self.assertEqual(login.status_code, 200)
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        with tempfile.TemporaryDirectory() as upload_directory, patch(
            "src.backend.routers.files.UPLOAD_DIR",
            upload_directory,
        ):
            upload = self.client.post(
                "/files/upload",
                headers=headers,
                files={"file": ("atleta.png", BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
            )
        self.assertEqual(upload.status_code, 200)

        athlete = self.client.post(
            "/deportistas/",
            headers=headers,
            json={
                "IDENTI_DEPORTISTA": "E2E-001",
                "TIPO_IDENTI": 1,
                "NOMBRE_DEPORTISTA": "Atleta E2E",
                "SEXO_DEPORTISTA": "F",
                "FECHA_NAC": "2000-01-01",
                "FOTO_DEPORTISTA": upload.json()["url"],
            },
        )
        entity = self.client.post(
            "/entidades/",
            headers=headers,
            json={"NIT_ENTIDAD": "E2E-CLUB", "RAZON_SOCIAL": "Club E2E"},
        )
        sport = self.client.post("/deportes/", headers=headers, json={"DEPORTE": "Prueba E2E"})
        self.assertEqual((athlete.status_code, entity.status_code, sport.status_code), (200, 200, 200))

        assignment = self.client.post(
            "/asignaciones/",
            headers=headers,
            json={
                "ID_DEPORTE": sport.json()["ID_DEPORTE"],
                "IDENTI_DEPORTISTA": "E2E-001",
                "NIT_ENTIDAD": "E2E-CLUB",
            },
        )
        valuation = self.client.post(
            "/somatotipo/",
            headers=headers,
            json={
                "IDENTI_DEPORTISTA": "E2E-001",
                "LOGIN_USER": "e2e",
                "FECHA_MEDIDA": "2026-06-20",
                "OBSERV": "Flujo E2E",
                "DETALLES": [MEASUREMENT],
            },
        )
        self.assertEqual((assignment.status_code, valuation.status_code), (200, 200))

        valuation_id = valuation.json()["id"]
        editable = self.client.get(f"/somatotipo/editable/{valuation_id}", headers=headers)
        detail_id = editable.json()["DETALLES"][0]["ID"]
        updated_measurement = {**MEASUREMENT, "PESO_kg": 66}
        update = self.client.put(
            f"/somatotipo/detalle/{detail_id}",
            headers=headers,
            json=updated_measurement,
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["PESO_kg"], 66.0)

        with self.SessionLocal() as database:
            database.add_all(
                [
                    valuation_view(valuation_id, date(2026, 6, 20), 66),
                    valuation_view(valuation_id + 1000, date(2026, 6, 21), 65),
                ]
            )
            database.commit()

        individual_pdf = self.client.get(f"/somatotipo/{valuation_id}/pdf", headers=headers)
        longitudinal_pdf = self.client.get(
            "/somatotipo/vista/deportista/E2E-001/longitudinal/pdf",
            headers=headers,
        )
        self.assertEqual((individual_pdf.status_code, longitudinal_pdf.status_code), (200, 200))
        self.assertTrue(individual_pdf.content.startswith(b"%PDF-1.4"))
        self.assertTrue(longitudinal_pdf.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"Atleta E2E", individual_pdf.content)
        self.assertIn(b"2026-06-21", longitudinal_pdf.content)
        self.assertNotEqual(individual_pdf.content, longitudinal_pdf.content)

        self.assertEqual(self.client.delete(f"/somatotipo/{valuation_id}", headers=headers).status_code, 200)
        self.assertEqual(
            self.client.delete(f"/asignaciones/{assignment.json()['id']}", headers=headers).status_code,
            200,
        )
        self.assertEqual(self.client.delete("/deportistas/E2E-001", headers=headers).status_code, 200)
        self.assertEqual(self.client.delete("/entidades/E2E-CLUB", headers=headers).status_code, 200)
        self.assertEqual(
            self.client.delete(f"/deportes/{sport.json()['ID_DEPORTE']}", headers=headers).status_code,
            200,
        )

        remaining = self.client.get("/deportistas/?search=E2E-001", headers=headers)
        self.assertEqual(remaining.status_code, 200)
        self.assertEqual(remaining.json()["total"], 0)
