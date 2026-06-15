from sqlalchemy.orm import Session

from ..models import Deportista, Deporte, DeporteDeportista, Entidad, Somatotipo
from .view_contract_service import get_somatotipo_view_contract


def serialize_recent_somatotipo(item: Somatotipo):
    athlete = getattr(item, "deportista", None)
    date_value = getattr(item, "FECHA_MEDIDA", None)
    return {
        "id_Somatotipo": getattr(item, "id_Somatotipo", None),
        "fecha": date_value.isoformat() if hasattr(date_value, "isoformat") else str(date_value or ""),
        "deportista_id": getattr(item, "IDENTI_DEPORTISTA", ""),
        "deportista": getattr(athlete, "NOMBRE_DEPORTISTA", "") or getattr(item, "IDENTI_DEPORTISTA", ""),
    }


def get_dashboard_summary(db: Session):
    recent_items = (
        db.query(Somatotipo)
        .order_by(Somatotipo.FECHA_MEDIDA.desc(), Somatotipo.id_Somatotipo.desc())
        .limit(6)
        .all()
    )
    return {
        "total_deportistas": db.query(Deportista).count(),
        "total_valoraciones": db.query(Somatotipo).count(),
        "total_deportes": db.query(Deporte).count(),
        "total_entidades": db.query(Entidad).count(),
        "total_asignaciones": db.query(DeporteDeportista).count(),
        "actividad_reciente": [serialize_recent_somatotipo(item) for item in recent_items],
        "vista_contrato": get_somatotipo_view_contract(db),
    }
