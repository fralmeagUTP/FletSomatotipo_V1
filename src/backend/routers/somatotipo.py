from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from ..database import get_db
from ..models import Somatotipo, SomatotipoDetalle, VistaValoracionCorporal

router = APIRouter(prefix="/somatotipo", tags=["Somatotipo"])

class SomatotipoDetalleBase(BaseModel):
    ESTA_USER_CM: float
    PESO_kg: float
    PLIEGUE_TRICIPITAL: float
    PLIEGUE_SUBESCAPULAR: float
    PLIEGUE_SUPRAILIACO: float
    PLIEGUE_ABDOMINAL: float
    PLIEGUE_MUSLO_ANT: float
    PLIEGUE_MEDIAL_PIERNA: float
    DIAMETRO_BIEPI_MUNECA: float
    DIAMETRO_BIEPI_FEMUR: float
    DIAMETRO_CODO: float
    PERIMETRO_BICED_CONTRAIDO: float
    PERIMETRO_PIERNA: float
    CIRCUNFERENCIA_CARPO: float

class SomatotipoCreate(BaseModel):
    IDENTI_DEPORTISTA: str
    LOGIN_USER: str
    FECHA_MEDIDA: date
    OBSERV: Optional[str] = ""
    DETALLES: List[SomatotipoDetalleBase]

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
    # 1. Create Header
    nuevo_header = Somatotipo(
        IDENTI_DEPORTISTA=s.IDENTI_DEPORTISTA,
        LOGIN_USER=s.LOGIN_USER,
        FECHA_MEDIDA=s.FECHA_MEDIDA,
        OBSERV=s.OBSERV
    )
    db.add(nuevo_header)
    db.commit()
    db.refresh(nuevo_header)
    
    # 2. Create Detail
    # 2. Create Details
    for detalle in s.DETALLES:
        nuevo_detalle = SomatotipoDetalle(
            id_Somatotipo=nuevo_header.id_Somatotipo,
            **detalle.dict()
        )
        db.add(nuevo_detalle)
        
    db.commit()
    
    return {"message": "Somatotipo registrado con éxito", "id": nuevo_header.id_Somatotipo}

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
    return db.query(Somatotipo).options(joinedload(Somatotipo.detalles)).filter(Somatotipo.IDENTI_DEPORTISTA == identi).all()
    
@router.get("/vista/deportista/{identi}")
def historial_vista(identi: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de mediciones usando la VISTA CDRVistaValoracionCorporal.
    """
    return db.query(VistaValoracionCorporal).filter(VistaValoracionCorporal.IDENTI_DEPORTISTA == identi).all()
