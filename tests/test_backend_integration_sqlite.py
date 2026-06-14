import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.database import Base
from src.backend.models import Deportista, DeporteDeportista, Entidad, Somatotipo, SomatotipoDetalle, VistaValoracionCorporal
from src.backend.schemas.entidades_deportes import DeporteCreate, DeporteDeportistaCreate, EntidadCreate
from src.backend.schemas.somatotipo import SomatotipoCreate, SomatotipoDetalleBase
from src.backend.services.deportistas_service import create_deportista, list_deportistas_page
from src.backend.services.entidades_deportes_service import (
    create_asignacion,
    create_deporte,
    create_entidad,
    delete_asignacion,
    list_asignaciones_page,
    list_deportes_page,
    list_entidades_page,
    update_asignacion,
    update_deporte,
    update_entidad,
)
from src.backend.services.somatotipo_service import (
    create_somatotipo,
    create_somatotipo_detalle,
    delete_somatotipo_detalle,
    get_historial_somatotipos,
    get_historial_vista_page,
    get_somatotipo_editable_or_404,
    list_somatotipos_editables,
    update_somatotipo_detalle,
)


class BackendSqliteIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_deportista_create_and_paginated_list_use_real_database(self):
        create_deportista(
            self.db,
            {
                "IDENTI_DEPORTISTA": "123",
                "TIPO_IDENTI": 1,
                "NOMBRE_DEPORTISTA": "Ana Perez",
                "SEXO_DEPORTISTA": "F",
                "FECHA_NAC": date(2000, 1, 1),
            },
        )

        result = list_deportistas_page(self.db, search="Ana", page=1, page_size=10)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0].IDENTI_DEPORTISTA, "123")

    def test_entidades_deportes_and_assignments_crud_use_real_database(self):
        self.db.add(
            Deportista(
                IDENTI_DEPORTISTA="123",
                TIPO_IDENTI=1,
                NOMBRE_DEPORTISTA="Ana Perez",
                SEXO_DEPORTISTA="F",
            )
        )
        self.db.commit()

        entidad = create_entidad(
            self.db,
            EntidadCreate(
                NIT_ENTIDAD="900",
                RAZON_SOCIAL="Club Deportivo",
                TELEFONO="300",
                CONTACTO="Laura",
                E_MAIL="club@example.com",
            ).model_dump(),
        )
        deporte = create_deporte(
            self.db,
            DeporteCreate(ID_DEPORTE=7, DEPORTE="Natación").model_dump(),
        )
        asignacion = create_asignacion(
            self.db,
            DeporteDeportistaCreate(
                ID_DEPORTE=deporte.ID_DEPORTE,
                IDENTI_DEPORTISTA="123",
                NIT_ENTIDAD=entidad.NIT_ENTIDAD,
            ).model_dump(),
        )

        updated_entidad = update_entidad(
            self.db,
            "900",
            EntidadCreate(NIT_ENTIDAD="900", RAZON_SOCIAL="Club Actualizado").model_dump(),
        )
        updated_deporte = update_deporte(
            self.db,
            7,
            DeporteCreate(DEPORTE="Natación carreras").model_dump(),
        )
        updated_asignacion = update_asignacion(
            self.db,
            asignacion.id,
            DeporteDeportistaCreate(ID_DEPORTE=7, IDENTI_DEPORTISTA="123", NIT_ENTIDAD="900").model_dump(),
        )

        self.assertEqual(list_entidades_page(self.db, "Club")["total"], 1)
        self.assertEqual(list_deportes_page(self.db, "Natación")["total"], 1)
        self.assertEqual(list_asignaciones_page(self.db, "Ana")["total"], 1)
        self.assertEqual(updated_entidad.RAZON_SOCIAL, "Club Actualizado")
        self.assertEqual(updated_deporte.DEPORTE, "Natación carreras")
        self.assertEqual(updated_asignacion.ID_DEPORTE, 7)

        delete_asignacion(self.db, asignacion.id)

        self.assertEqual(self.db.query(DeporteDeportista).count(), 0)
        self.assertEqual(self.db.query(Entidad).count(), 1)

    def test_somatotipo_create_persists_header_and_detail(self):
        self.db.add(
            Deportista(
                IDENTI_DEPORTISTA="123",
                TIPO_IDENTI=1,
                NOMBRE_DEPORTISTA="Ana Perez",
                SEXO_DEPORTISTA="F",
            )
        )
        self.db.commit()

        payload = SomatotipoCreate(
            IDENTI_DEPORTISTA="123",
            LOGIN_USER="admin",
            FECHA_MEDIDA=date.today(),
            OBSERV="Control",
            DETALLES=[
                {
                    "ESTA_USER_CM": 170,
                    "PESO_kg": 65,
                    "PLIEGUE_TRICIPITAL": 10,
                    "PLIEGUE_SUBESCAPULAR": 11,
                    "PLIEGUE_SUPRAILIACO": 12,
                    "PLIEGUE_ABDOMINAL": 13,
                    "PLIEGUE_MUSLO_ANT": 14,
                    "PLIEGUE_MEDIAL_PIERNA": 15,
                    "DIAMETRO_BIEPI_MUNECA": 6,
                    "DIAMETRO_BIEPI_FEMUR": 9,
                    "DIAMETRO_CODO": 7,
                    "PERIMETRO_BICED_CONTRAIDO": 32,
                    "PERIMETRO_PIERNA": 40,
                    "CIRCUNFERENCIA_CARPO": 17,
                }
            ],
        )

        result = create_somatotipo(self.db, payload)

        self.assertEqual(self.db.query(Somatotipo).count(), 1)
        self.assertEqual(self.db.query(SomatotipoDetalle).count(), 1)
        self.assertEqual(result["id"], self.db.query(Somatotipo).first().id_Somatotipo)

        history = get_historial_somatotipos(self.db, "123")
        self.assertEqual(len(history), 1)
        self.assertEqual(len(history[0].detalles), 1)

    def test_editable_somatotipo_list_load_and_update_detail(self):
        self.db.add(
            Deportista(
                IDENTI_DEPORTISTA="123",
                TIPO_IDENTI=1,
                NOMBRE_DEPORTISTA="Ana Perez",
                SEXO_DEPORTISTA="F",
            )
        )
        self.db.commit()
        payload = SomatotipoCreate(
            IDENTI_DEPORTISTA="123",
            LOGIN_USER="admin",
            FECHA_MEDIDA=date.today(),
            OBSERV="Control",
            DETALLES=[
                {
                    "ESTA_USER_CM": 170,
                    "PESO_kg": 65,
                    "PLIEGUE_TRICIPITAL": 10,
                    "PLIEGUE_SUBESCAPULAR": 11,
                    "PLIEGUE_SUPRAILIACO": 12,
                    "PLIEGUE_ABDOMINAL": 13,
                    "PLIEGUE_MUSLO_ANT": 14,
                    "PLIEGUE_MEDIAL_PIERNA": 15,
                    "DIAMETRO_BIEPI_MUNECA": 6,
                    "DIAMETRO_BIEPI_FEMUR": 9,
                    "DIAMETRO_CODO": 7,
                    "PERIMETRO_BICED_CONTRAIDO": 32,
                    "PERIMETRO_PIERNA": 40,
                    "CIRCUNFERENCIA_CARPO": 17,
                }
            ],
        )
        created = create_somatotipo(self.db, payload)
        detail_id = self.db.query(SomatotipoDetalle).first().ID

        listed = list_somatotipos_editables(self.db, "123")
        loaded = get_somatotipo_editable_or_404(self.db, created["id"])
        updated = update_somatotipo_detalle(
            self.db,
            detail_id,
            SomatotipoDetalleBase(
                ESTA_USER_CM=171,
                PESO_kg=70,
                PLIEGUE_TRICIPITAL=10,
                PLIEGUE_SUBESCAPULAR=11,
                PLIEGUE_SUPRAILIACO=12,
                PLIEGUE_ABDOMINAL=13,
                PLIEGUE_MUSLO_ANT=14,
                PLIEGUE_MEDIAL_PIERNA=15,
                DIAMETRO_BIEPI_MUNECA=6,
                DIAMETRO_BIEPI_FEMUR=9,
                DIAMETRO_CODO=7,
                PERIMETRO_BICED_CONTRAIDO=32,
                PERIMETRO_PIERNA=40,
                CIRCUNFERENCIA_CARPO=17,
            ),
        )
        created_detail = create_somatotipo_detalle(
            self.db,
            created["id"],
            SomatotipoDetalleBase(
                ESTA_USER_CM=172,
                PESO_kg=71,
                PLIEGUE_TRICIPITAL=10,
                PLIEGUE_SUBESCAPULAR=11,
                PLIEGUE_SUPRAILIACO=12,
                PLIEGUE_ABDOMINAL=13,
                PLIEGUE_MUSLO_ANT=14,
                PLIEGUE_MEDIAL_PIERNA=15,
                DIAMETRO_BIEPI_MUNECA=6,
                DIAMETRO_BIEPI_FEMUR=9,
                DIAMETRO_CODO=7,
                PERIMETRO_BICED_CONTRAIDO=32,
                PERIMETRO_PIERNA=40,
                CIRCUNFERENCIA_CARPO=17,
            ),
        )
        delete_result = delete_somatotipo_detalle(self.db, detail_id)

        self.assertEqual(listed[0]["DETALLES"][0]["ID"], detail_id)
        self.assertEqual(loaded["id_Somatotipo"], created["id"])
        self.assertEqual(updated["PESO_kg"], 70.0)
        self.assertEqual(created_detail["PESO_kg"], 71.0)
        self.assertEqual(delete_result["ID"], detail_id)
        self.assertEqual(self.db.query(Somatotipo).count(), 1)
        self.assertEqual(self.db.query(SomatotipoDetalle).count(), 1)

    def test_historial_vista_paginated_list_uses_real_database(self):
        self.db.add_all(
            [
                VistaValoracionCorporal(
                    id_Somatotipo=1,
                    IDENTI_DEPORTISTA="123",
                    NOMBRE_DEPORTISTA="Ana",
                    FECHA_MEDIDA=date(2026, 6, 1),
                    ESTA_USER_CM=170,
                    PESO_kg=65,
                ),
                VistaValoracionCorporal(
                    id_Somatotipo=2,
                    IDENTI_DEPORTISTA="123",
                    NOMBRE_DEPORTISTA="Ana",
                    FECHA_MEDIDA=date(2026, 6, 2),
                    ESTA_USER_CM=171,
                    PESO_kg=66,
                ),
            ]
        )
        self.db.commit()

        result = get_historial_vista_page(self.db, "123", page=1, page_size=1)

        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id_Somatotipo"], 2)


if __name__ == "__main__":
    unittest.main()
