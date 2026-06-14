from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.anthropometry import MEASUREMENT_RULES


def measurement_field(field_name: str):
    rule = MEASUREMENT_RULES[field_name]
    return Field(gt=rule.minimum_exclusive, le=rule.maximum_inclusive)


class SomatotipoDetalleBase(BaseModel):
    ESTA_USER_CM: float = measurement_field("ESTA_USER_CM")
    PESO_kg: float = measurement_field("PESO_kg")
    PLIEGUE_TRICIPITAL: float = measurement_field("PLIEGUE_TRICIPITAL")
    PLIEGUE_SUBESCAPULAR: float = measurement_field("PLIEGUE_SUBESCAPULAR")
    PLIEGUE_SUPRAILIACO: float = measurement_field("PLIEGUE_SUPRAILIACO")
    PLIEGUE_ABDOMINAL: float = measurement_field("PLIEGUE_ABDOMINAL")
    PLIEGUE_MUSLO_ANT: float = measurement_field("PLIEGUE_MUSLO_ANT")
    PLIEGUE_MEDIAL_PIERNA: float = measurement_field("PLIEGUE_MEDIAL_PIERNA")
    DIAMETRO_BIEPI_MUNECA: float = measurement_field("DIAMETRO_BIEPI_MUNECA")
    DIAMETRO_BIEPI_FEMUR: float = measurement_field("DIAMETRO_BIEPI_FEMUR")
    DIAMETRO_CODO: float = measurement_field("DIAMETRO_CODO")
    PERIMETRO_BICED_CONTRAIDO: float = measurement_field("PERIMETRO_BICED_CONTRAIDO")
    PERIMETRO_PIERNA: float = measurement_field("PERIMETRO_PIERNA")
    CIRCUNFERENCIA_CARPO: float = measurement_field("CIRCUNFERENCIA_CARPO")


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
