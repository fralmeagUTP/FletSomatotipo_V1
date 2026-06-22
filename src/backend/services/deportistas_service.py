from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Deportista, DeporteDeportista, Somatotipo


def list_deportistas(db: Session, search: str | None = None, limit: int = 50):
    query = db.query(Deportista)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Deportista.NOMBRE_DEPORTISTA.ilike(search_filter),
                Deportista.IDENTI_DEPORTISTA.ilike(search_filter),
            )
        )
    return query.limit(limit).all()


def list_deportistas_page(db: Session, search: str | None = None, page: int = 1, page_size: int = 50):
    query = db.query(Deportista)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Deportista.NOMBRE_DEPORTISTA.ilike(search_filter),
                Deportista.IDENTI_DEPORTISTA.ilike(search_filter),
            )
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_deportista_or_404(db: Session, identi: str):
    deportista = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == identi).first()
    if not deportista:
        raise HTTPException(status_code=404, detail="Deportista no encontrado")
    return deportista


def create_deportista(db: Session, data: dict):
    existing = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == data["IDENTI_DEPORTISTA"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un deportista con esa identificación")

    try:
        deportista = Deportista(**data)
        db.add(deportista)
        db.commit()
        db.refresh(deportista)
        return deportista
    except Exception:
        db.rollback()
        raise


def update_deportista(db: Session, identi: str, data: dict):
    deportista = get_deportista_or_404(db, identi)
    if data.get("IDENTI_DEPORTISTA") != identi:
        raise HTTPException(
            status_code=409,
            detail="La identificación del deportista no se puede modificar; cree un registro nuevo si necesita cambiarla",
        )
    try:
        for key, value in data.items():
            setattr(deportista, key, value)

        db.commit()
        db.refresh(deportista)
        return deportista
    except Exception:
        db.rollback()
        raise


def delete_deportista(db: Session, identi: str):
    deportista = get_deportista_or_404(db, identi)
    assignment_count = (
        db.query(DeporteDeportista)
        .filter(DeporteDeportista.IDENTI_DEPORTISTA == identi)
        .count()
    )
    valuation_count = db.query(Somatotipo).filter(Somatotipo.IDENTI_DEPORTISTA == identi).count()
    if assignment_count or valuation_count:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el deportista porque tiene "
                f"{assignment_count} asignación(es) y {valuation_count} valoración(es) asociadas. "
                "Elimine primero las dependencias"
            ),
        )
    try:
        db.delete(deportista)
        db.commit()
        return {"message": "Deportista eliminado correctamente"}
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el deportista porque tiene datos asociados",
        ) from error
    except Exception:
        db.rollback()
        raise
