from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError


SOMATOTIPO_VIEW_NAME = "CDRVistaValoracionCorporal"

EXPECTED_SOMATOTIPO_VIEW_COLUMNS = [
    "id_Somatotipo",
    "FECHA_MEDIDA",
    "IDENTI_DEPORTISTA",
    "NOMBRE_DEPORTISTA",
    "ESTA_USER_CM",
    "PESO_kg",
    "PLIEGUE_TRICIPITAL",
    "PLIEGUE_SUBESCAPULAR",
    "PLIEGUE_SUPRAILIACO",
    "PLIEGUE_ABDOMINAL",
    "PLIEGUE_MUSLO_ANT",
    "PLIEGUE_MEDIAL_PIERNA",
    "DIAMETRO_BIEPI_MUNECA",
    "DIAMETRO_BIEPI_FEMUR",
    "DIAMETRO_CODO",
    "PERIMETRO_BICED_CONTRAIDO",
    "PERIMETRO_PIERNA",
    "CIRCUNFERENCIA_CARPO",
    "EDAD",
    "SEXO_DEPORTISTA",
    "PorcGrasoJonson",
    "PesoGrasoJhonston",
    "PorcGrasoFaulker",
    "PesoRasoFaulker",
    "PorcRasoYuasz",
    "PesoRasoYuazs",
    "PesoOseo",
    "PesoResidual",
    "Mma",
    "IMC",
    "EstadoIMC",
    "Complexion",
    "TipoComplexion",
    "Endomorfismo",
    "EscalaEndomorfismo",
    "Mesomorfismo",
    "EscalaMesomorfismo",
    "Ectomorfismo",
    "EscalaEctomorfismo",
    "X",
    "Y",
]


def evaluate_contract(available_columns: list[str]):
    expected = set(EXPECTED_SOMATOTIPO_VIEW_COLUMNS)
    available = set(available_columns)
    missing = sorted(expected - available)
    extra = sorted(available - expected)
    return {
        "view": SOMATOTIPO_VIEW_NAME,
        "ok": not missing,
        "expected_count": len(EXPECTED_SOMATOTIPO_VIEW_COLUMNS),
        "available_count": len(available_columns),
        "missing": missing,
        "extra": extra,
        "error": None,
    }


def get_somatotipo_view_contract(db):
    try:
        inspector = inspect(db.bind)
        columns = [column["name"] for column in inspector.get_columns(SOMATOTIPO_VIEW_NAME)]
        return evaluate_contract(columns)
    except SQLAlchemyError as error:
        return {
            "view": SOMATOTIPO_VIEW_NAME,
            "ok": False,
            "expected_count": len(EXPECTED_SOMATOTIPO_VIEW_COLUMNS),
            "available_count": 0,
            "missing": EXPECTED_SOMATOTIPO_VIEW_COLUMNS,
            "extra": [],
            "error": str(error),
        }
