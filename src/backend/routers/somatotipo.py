from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth_utils import get_current_user
from ..schemas.somatotipo import SomatotipoCreate
from ..services import somatotipo_service

router = APIRouter(prefix="/somatotipo", tags=["Somatotipo"], dependencies=[Depends(get_current_user)])

@router.post("/")
def registrar_somatotipo(s: SomatotipoCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo cálculo de somatotipo para un deportista.

    Guarda tanto el encabezado (fecha, observaciones) como el detalle (mediciones).

    Args:
        s (SomatotipoCreate): Datos del somatotipo y mediciones.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Mensaje de éxito e ID del nuevo registro.
    """
    return somatotipo_service.create_somatotipo(db, s)

@router.get("/deportista/{identi}")
def historial_somatotipos(identi: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de mediciones de somatotipo de un deportista.

    Args:
        identi (str): Identificación del deportista.
        db (Session): Sesión de base de datos.
    
    Returns:
        List[Somatotipo]: Lista de registros de somatotipo.
    """
    return somatotipo_service.get_historial_somatotipos(db, identi)
    
@router.get("/vista/deportista/{identi}")
def historial_vista(
    identi: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    Obtiene el historial de mediciones usando la VISTA CDRVistaValoracionCorporal.
    """
    return somatotipo_service.get_historial_vista_page(
        db,
        identi,
        page=max(page, 1),
        page_size=min(max(page_size, 1), 100),
    )

@router.delete("/{id_somatotipo}")
def delete_somatotipo(id_somatotipo: int, db: Session = Depends(get_db)):
    """
    Elimina un registro de somatotipo y todos sus detalles asociados.
    """
    return somatotipo_service.delete_somatotipo(db, id_somatotipo)
