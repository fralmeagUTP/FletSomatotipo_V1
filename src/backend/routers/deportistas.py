from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..auth_utils import get_current_user
from ..schemas.deportistas import DeportistaCreate, DeportistaPage, DeportistaResponse
from ..services import deportistas_service

router = APIRouter(prefix="/deportistas", tags=["Deportistas"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=DeportistaPage)
def listar_deportistas(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    """
    Lista los deportistas registrados, opcionalmente filtrando por nombre o identificación.

    Args:
        search (Optional[str]): Término de búsqueda (nombre o identificación).
        db (Session): Sesión de base de datos.
    
    Returns:
        List[DeportistaResponse]: Lista de deportistas (máximo 50).
    """
    return deportistas_service.list_deportistas_page(db, search, page=max(page, 1), page_size=min(max(page_size, 1), 100))

@router.get("/{identi}", response_model=DeportistaResponse)
def obtener_deportista(identi: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un deportista por su identificación.

    Args:
        identi (str): Identificación del deportista.
        db (Session): Sesión de base de datos.

    Returns:
        DeportistaResponse: Objeto deportista encontrado.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    return deportistas_service.get_deportista_or_404(db, identi)

@router.post("/", response_model=DeportistaResponse)
def crear_deportista(d: DeportistaCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo deportista en el sistema.

    Args:
        d (DeportistaCreate): Datos del nuevo deportista.
        db (Session): Sesión de base de datos.
    
    Returns:
        DeportistaResponse: El deportista creado.

    Raises:
        HTTPException: Si ya existe un deportista con la misma identificación.
    """
    return deportistas_service.create_deportista(db, d.model_dump())

@router.put("/{identi}", response_model=DeportistaResponse)
def actualizar_deportista(identi: str, d: DeportistaCreate, db: Session = Depends(get_db)):
    """
    Actualiza los datos de un deportista existente.

    Args:
        identi (str): Identificación del deportista a actualizar.
        d (DeportistaCreate): Nuevos datos del deportista.
        db (Session): Sesión de base de datos.

    Returns:
        DeportistaResponse: El deportista actualizado.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    return deportistas_service.update_deportista(db, identi, d.model_dump())

@router.delete("/{identi}")
def eliminar_deportista(identi: str, db: Session = Depends(get_db)):
    """
    Elimina un deportista de la base de datos.
    
    Args:
        identi (str): Identificación del deportista a eliminar.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    return deportistas_service.delete_deportista(db, identi)
