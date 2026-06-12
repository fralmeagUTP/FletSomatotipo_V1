from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..schemas.entidades_deportes import (
    DeporteCreate,
    DeporteDeportistaCreate,
    DeporteDeportistaPage,
    DeporteDeportistaResponse,
    DeportePage,
    DeporteResponse,
    EntidadCreate,
    EntidadPage,
    EntidadResponse,
)
from ..services import entidades_deportes_service


router = APIRouter(tags=["Entidades y Deportes"], dependencies=[Depends(get_current_user)])


@router.get("/entidades/", response_model=EntidadPage)
def listar_entidades(search: str | None = None, page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    return entidades_deportes_service.list_entidades_page(
        db,
        search,
        page=max(page, 1),
        page_size=min(max(page_size, 1), 100),
    )


@router.post("/entidades/", response_model=EntidadResponse)
def crear_entidad(entidad: EntidadCreate, db: Session = Depends(get_db)):
    return entidades_deportes_service.create_entidad(db, entidad.model_dump())


@router.put("/entidades/{nit}", response_model=EntidadResponse)
def actualizar_entidad(nit: str, entidad: EntidadCreate, db: Session = Depends(get_db)):
    return entidades_deportes_service.update_entidad(db, nit, entidad.model_dump())


@router.delete("/entidades/{nit}")
def eliminar_entidad(nit: str, db: Session = Depends(get_db)):
    return entidades_deportes_service.delete_entidad(db, nit)


@router.get("/deportes/", response_model=DeportePage)
def listar_deportes(search: str | None = None, page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    return entidades_deportes_service.list_deportes_page(
        db,
        search,
        page=max(page, 1),
        page_size=min(max(page_size, 1), 100),
    )


@router.post("/deportes/", response_model=DeporteResponse)
def crear_deporte(deporte: DeporteCreate, db: Session = Depends(get_db)):
    return entidades_deportes_service.create_deporte(db, deporte.model_dump())


@router.put("/deportes/{deporte_id}", response_model=DeporteResponse)
def actualizar_deporte(deporte_id: int, deporte: DeporteCreate, db: Session = Depends(get_db)):
    return entidades_deportes_service.update_deporte(db, deporte_id, deporte.model_dump())


@router.delete("/deportes/{deporte_id}")
def eliminar_deporte(deporte_id: int, db: Session = Depends(get_db)):
    return entidades_deportes_service.delete_deporte(db, deporte_id)


@router.get("/asignaciones/", response_model=DeporteDeportistaPage)
def listar_asignaciones(search: str | None = None, page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    return entidades_deportes_service.list_asignaciones_page(
        db,
        search,
        page=max(page, 1),
        page_size=min(max(page_size, 1), 100),
    )


@router.post("/asignaciones/", response_model=DeporteDeportistaResponse)
def crear_asignacion(asignacion: DeporteDeportistaCreate, db: Session = Depends(get_db)):
    return entidades_deportes_service.create_asignacion(db, asignacion.model_dump())


@router.put("/asignaciones/{assignment_id}", response_model=DeporteDeportistaResponse)
def actualizar_asignacion(
    assignment_id: int,
    asignacion: DeporteDeportistaCreate,
    db: Session = Depends(get_db),
):
    return entidades_deportes_service.update_asignacion(db, assignment_id, asignacion.model_dump())


@router.delete("/asignaciones/{assignment_id}")
def eliminar_asignacion(assignment_id: int, db: Session = Depends(get_db)):
    return entidades_deportes_service.delete_asignacion(db, assignment_id)
