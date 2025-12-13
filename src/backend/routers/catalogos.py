from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TipoDocumento, Estrato, NivelEducativo

router = APIRouter(prefix="/catalogos", tags=["Catalogos"])

@router.get("/tipos_documento")
def get_tipos_documento(db: Session = Depends(get_db)):
    """
    Obtiene la lista de tipos de documentos de identidad disponibles.

    Args:
        db (Session): Sesión de base de datos.

    Returns:
        List[TipoDocumento]: Lista de tipos de documentos.
    """
    return db.query(TipoDocumento).all()

@router.get("/estratos")
def get_estratos(db: Session = Depends(get_db)):
    """
    Obtiene la lista de estratos socioeconómicos.

    Args:
        db (Session): Sesión de base de datos.
    
    Returns:
        List[Estrato]: Lista de estratos.
    """
    return db.query(Estrato).all()

@router.get("/niveles_educativos")
def get_niveles_educativos(db: Session = Depends(get_db)):
    """
    Obtiene la lista de niveles educativos.

    Args:
        db (Session): Sesión de base de datos.

    Returns:
        List[NivelEducativo]: Lista de niveles educativos.
    """
    return db.query(NivelEducativo).all()
