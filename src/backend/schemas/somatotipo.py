from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SomatotipoDetalleBase(BaseModel):
    ESTA_USER_CM: float = Field(gt=50, le=250)
    PESO_kg: float = Field(gt=10, le=300)
    PLIEGUE_TRICIPITAL: float = Field(gt=0, le=100)
    PLIEGUE_SUBESCAPULAR: float = Field(gt=0, le=100)
    PLIEGUE_SUPRAILIACO: float = Field(gt=0, le=100)
    PLIEGUE_ABDOMINAL: float = Field(gt=0, le=100)
    PLIEGUE_MUSLO_ANT: float = Field(gt=0, le=100)
    PLIEGUE_MEDIAL_PIERNA: float = Field(gt=0, le=100)
    DIAMETRO_BIEPI_MUNECA: float = Field(gt=0, le=200)
    DIAMETRO_BIEPI_FEMUR: float = Field(gt=0, le=200)
    DIAMETRO_CODO: float = Field(gt=0, le=200)
    PERIMETRO_BICED_CONTRAIDO: float = Field(gt=0, le=250)
    PERIMETRO_PIERNA: float = Field(gt=0, le=250)
    CIRCUNFERENCIA_CARPO: float = Field(gt=0, le=200)


class SomatotipoCreate(BaseModel):
    IDENTI_DEPORTISTA: str = Field(min_length=1, max_length=20)
    LOGIN_USER: str = Field(min_length=1, max_length=60)
    FECHA_MEDIDA: date
    OBSERV: Optional[str] = ""
    DETALLES: List[SomatotipoDetalleBase] = Field(min_length=1)

    @field_validator("IDENTI_DEPORTISTA", "LOGIN_USER")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("OBSERV", mode="before")
    @classmethod
    def normalize_observ(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("FECHA_MEDIDA")
    @classmethod
    def validate_measure_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La fecha de medida no puede estar en el futuro")
        return value
