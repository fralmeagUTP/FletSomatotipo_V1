from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..models import Somatotipo, SomatotipoDetalle, VistaValoracionCorporal


def create_somatotipo(db: Session, data):
    try:
        header = Somatotipo(
            IDENTI_DEPORTISTA=data.IDENTI_DEPORTISTA,
            LOGIN_USER=data.LOGIN_USER,
            FECHA_MEDIDA=data.FECHA_MEDIDA,
            OBSERV=data.OBSERV,
        )
        db.add(header)
        db.flush()

        for detail in data.DETALLES:
            db.add(
                SomatotipoDetalle(
                    id_Somatotipo=header.id_Somatotipo,
                    **detail.model_dump(),
                )
            )

        db.commit()
        db.refresh(header)
        return {"message": "Somatotipo registrado con éxito", "id": header.id_Somatotipo}
    except Exception:
        db.rollback()
        raise


def get_historial_somatotipos(db: Session, identi: str):
    return (
        db.query(Somatotipo)
        .options(joinedload(Somatotipo.detalles))
        .filter(Somatotipo.IDENTI_DEPORTISTA == identi)
        .all()
    )


def get_historial_vista(db: Session, identi: str):
    return db.query(VistaValoracionCorporal).filter(VistaValoracionCorporal.IDENTI_DEPORTISTA == identi).all()


def get_historial_vista_page(db: Session, identi: str, page: int = 1, page_size: int = 20):
    query = db.query(VistaValoracionCorporal).filter(VistaValoracionCorporal.IDENTI_DEPORTISTA == identi)
    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query.order_by(VistaValoracionCorporal.FECHA_MEDIDA.desc(), VistaValoracionCorporal.id_Somatotipo.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def delete_somatotipo(db: Session, id_somatotipo: int):
    somatotipo = db.query(Somatotipo).filter(Somatotipo.id_Somatotipo == id_somatotipo).first()
    if not somatotipo:
        raise HTTPException(status_code=404, detail="Somatotipo no encontrado")

    try:
        db.query(SomatotipoDetalle).filter(SomatotipoDetalle.id_Somatotipo == id_somatotipo).delete()
        db.delete(somatotipo)
        db.commit()
        return {"message": "Somatotipo eliminado con éxito"}
    except Exception:
        db.rollback()
        raise
