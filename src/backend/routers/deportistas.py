from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date
from ..database import get_db
from ..models import Deportista, TipoDocumento, Estrato, NivelEducativo

router = APIRouter(prefix="/deportistas", tags=["Deportistas"])

# Pydantic models for request/response
class DeportistaCreate(BaseModel):
    IDENTI_DEPORTISTA: str
    TIPO_IDENTI: int
    NOMBRE_DEPORTISTA: str
    SEXO_DEPORTISTA: str
    FECHA_NAC: Optional[date] = None
    CIUDAD_NAC: Optional[str] = None
    DEPARTA_NAC: Optional[str] = None
    PAIS_NAC: Optional[str] = None
    DEPARTA_RESI: Optional[str] = None
    CIUDAD_RESI: Optional[str] = None
    DIRECC_RESI: Optional[str] = None
    TELEFONO: Optional[str] = None
    E_MAIL: Optional[str] = None
    ID_ESTRATO: Optional[int] = None
    ID_NIVEL: Optional[int] = None
    NOMBRE_INSTITU: Optional[str] = None
    OBSERVACIONES: Optional[str] = None

class DeportistaResponse(DeportistaCreate):
    FOTO_DEPORTISTA: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[DeportistaResponse])
def listar_deportistas(search: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Lista los deportistas registrados, opcionalmente filtrando por nombre o identificación.

    Args:
        search (Optional[str]): Término de búsqueda (nombre o identificación).
        db (Session): Sesión de base de datos.
    
    Returns:
        List[DeportistaResponse]: Lista de deportistas (máximo 50).
    """
    query = db.query(Deportista)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Deportista.NOMBRE_DEPORTISTA.ilike(search_filter),
                Deportista.IDENTI_DEPORTISTA.ilike(search_filter)
            )
        )
    return query.limit(50).all()

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
    deportista = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == identi).first()
    if not deportista:
        raise HTTPException(status_code=404, detail="Deportista no encontrado")
    return deportista

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
    existing = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == d.IDENTI_DEPORTISTA).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un deportista con esa identificación")
    
    nuevo_deportista = Deportista(**d.dict())
    db.add(nuevo_deportista)
    db.commit()
    db.refresh(nuevo_deportista)
    return nuevo_deportista

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
    deportista = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == identi).first()
    if not deportista:
        raise HTTPException(status_code=404, detail="Deportista no encontrado")
    
    for key, value in d.dict().items():
        setattr(deportista, key, value)
    
    db.commit()
    db.refresh(deportista)
    return deportista

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
    deportista = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == identi).first()
    if not deportista:
        raise HTTPException(status_code=404, detail="Deportista no encontrado")
    
    # Check for dependencies (Somatotipos) before delete could be added here
    db.delete(deportista)
    db.commit()
    return {"message": "Deportista eliminado correctamente"}
