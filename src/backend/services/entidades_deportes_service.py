from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models import Deportista, Deporte, DeporteDeportista, Entidad


def page_response(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def list_entidades_page(db: Session, search: str | None = None, page: int = 1, page_size: int = 50):
    query = db.query(Entidad)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Entidad.NIT_ENTIDAD.ilike(search_filter),
                Entidad.RAZON_SOCIAL.ilike(search_filter),
                Entidad.CONTACTO.ilike(search_filter),
            )
        )
    return page_response(query.order_by(Entidad.RAZON_SOCIAL), page, page_size)


def get_entidad_or_404(db: Session, nit: str):
    entidad = db.query(Entidad).filter(Entidad.NIT_ENTIDAD == nit).first()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return entidad


def create_entidad(db: Session, data: dict):
    if db.query(Entidad).filter(Entidad.NIT_ENTIDAD == data["NIT_ENTIDAD"]).first():
        raise HTTPException(status_code=400, detail="Ya existe una entidad con ese NIT")
    try:
        entidad = Entidad(**data)
        db.add(entidad)
        db.commit()
        db.refresh(entidad)
        return entidad
    except Exception:
        db.rollback()
        raise


def update_entidad(db: Session, nit: str, data: dict):
    entidad = get_entidad_or_404(db, nit)
    if data["NIT_ENTIDAD"] != nit and db.query(Entidad).filter(Entidad.NIT_ENTIDAD == data["NIT_ENTIDAD"]).first():
        raise HTTPException(status_code=400, detail="Ya existe una entidad con ese NIT")
    try:
        for field, value in data.items():
            setattr(entidad, field, value)
        db.commit()
        db.refresh(entidad)
        return entidad
    except Exception:
        db.rollback()
        raise


def delete_entidad(db: Session, nit: str):
    entidad = get_entidad_or_404(db, nit)
    try:
        db.delete(entidad)
        db.commit()
        return {"message": "Entidad eliminada correctamente"}
    except Exception:
        db.rollback()
        raise


def list_deportes_page(db: Session, search: str | None = None, page: int = 1, page_size: int = 50):
    query = db.query(Deporte)
    if search:
        query = query.filter(Deporte.DEPORTE.ilike(f"%{search}%"))
    return page_response(query.order_by(Deporte.DEPORTE), page, page_size)


def get_deporte_or_404(db: Session, deporte_id: int):
    deporte = db.query(Deporte).filter(Deporte.ID_DEPORTE == deporte_id).first()
    if not deporte:
        raise HTTPException(status_code=404, detail="Deporte no encontrado")
    return deporte


def create_deporte(db: Session, data: dict):
    payload = {key: value for key, value in data.items() if value is not None}
    if payload.get("ID_DEPORTE") and db.query(Deporte).filter(Deporte.ID_DEPORTE == payload["ID_DEPORTE"]).first():
        raise HTTPException(status_code=400, detail="Ya existe un deporte con ese ID")
    try:
        deporte = Deporte(**payload)
        db.add(deporte)
        db.commit()
        db.refresh(deporte)
        return deporte
    except Exception:
        db.rollback()
        raise


def update_deporte(db: Session, deporte_id: int, data: dict):
    deporte = get_deporte_or_404(db, deporte_id)
    try:
        deporte.DEPORTE = data["DEPORTE"]
        db.commit()
        db.refresh(deporte)
        return deporte
    except Exception:
        db.rollback()
        raise


def delete_deporte(db: Session, deporte_id: int):
    deporte = get_deporte_or_404(db, deporte_id)
    try:
        db.delete(deporte)
        db.commit()
        return {"message": "Deporte eliminado correctamente"}
    except Exception:
        db.rollback()
        raise


def validate_assignment_refs(db: Session, data: dict):
    get_deporte_or_404(db, data["ID_DEPORTE"])
    if not db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == data["IDENTI_DEPORTISTA"]).first():
        raise HTTPException(status_code=404, detail="Deportista no encontrado")
    get_entidad_or_404(db, data["NIT_ENTIDAD"])


def list_asignaciones_page(db: Session, search: str | None = None, page: int = 1, page_size: int = 50):
    query = db.query(DeporteDeportista)
    if search:
        search_filter = f"%{search}%"
        query = (
            query.outerjoin(Deporte, Deporte.ID_DEPORTE == DeporteDeportista.ID_DEPORTE)
            .outerjoin(Deportista, Deportista.IDENTI_DEPORTISTA == DeporteDeportista.IDENTI_DEPORTISTA)
            .outerjoin(Entidad, Entidad.NIT_ENTIDAD == DeporteDeportista.NIT_ENTIDAD)
            .filter(
                or_(
                    Deporte.DEPORTE.ilike(search_filter),
                    Deportista.NOMBRE_DEPORTISTA.ilike(search_filter),
                    DeporteDeportista.IDENTI_DEPORTISTA.ilike(search_filter),
                    Entidad.RAZON_SOCIAL.ilike(search_filter),
                    DeporteDeportista.NIT_ENTIDAD.ilike(search_filter),
                )
            )
        )
    return page_response(query.order_by(DeporteDeportista.id.desc()), page, page_size)


def get_asignacion_or_404(db: Session, assignment_id: int):
    assignment = db.query(DeporteDeportista).filter(DeporteDeportista.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return assignment


def create_asignacion(db: Session, data: dict):
    validate_assignment_refs(db, data)
    try:
        assignment = DeporteDeportista(**data)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    except Exception:
        db.rollback()
        raise


def update_asignacion(db: Session, assignment_id: int, data: dict):
    assignment = get_asignacion_or_404(db, assignment_id)
    validate_assignment_refs(db, data)
    try:
        for field, value in data.items():
            setattr(assignment, field, value)
        db.commit()
        db.refresh(assignment)
        return assignment
    except Exception:
        db.rollback()
        raise


def delete_asignacion(db: Session, assignment_id: int):
    assignment = get_asignacion_or_404(db, assignment_id)
    try:
        db.delete(assignment)
        db.commit()
        return {"message": "Asignación eliminada correctamente"}
    except Exception:
        db.rollback()
        raise
