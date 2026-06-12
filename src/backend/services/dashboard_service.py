from sqlalchemy.orm import Session

from ..models import Deportista, Somatotipo
from .view_contract_service import get_somatotipo_view_contract


def get_dashboard_summary(db: Session):
    return {
        "total_deportistas": db.query(Deportista).count(),
        "total_valoraciones": db.query(Somatotipo).count(),
        "vista_contrato": get_somatotipo_view_contract(db),
    }
