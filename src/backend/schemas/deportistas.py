from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class DeportistaCreate(BaseModel):
    IDENTI_DEPORTISTA: str = Field(min_length=1, max_length=20)
    TIPO_IDENTI: int = Field(gt=0)
    NOMBRE_DEPORTISTA: str = Field(min_length=1, max_length=50)
    FOTO_DEPORTISTA: Optional[str] = None
    SEXO_DEPORTISTA: str
    FECHA_NAC: Optional[date] = None
    CIUDAD_NAC: Optional[str] = None
    DEPARTA_NAC: Optional[str] = None
    PAIS_NAC: Optional[str] = None
    DEPARTA_RESI: Optional[str] = None
    CIUDAD_RESI: Optional[str] = None
    DIRECC_RESI: Optional[str] = None
    TELEFONO: Optional[str] = None
    E_MAIL: Optional[EmailStr] = None
    ID_ESTRATO: Optional[int] = None
    ID_NIVEL: Optional[int] = None
    NOMBRE_INSTITU: Optional[str] = None
    OBSERVACIONES: Optional[str] = None

    @field_validator("IDENTI_DEPORTISTA", "NOMBRE_DEPORTISTA", "SEXO_DEPORTISTA")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator(
        "CIUDAD_NAC",
        "DEPARTA_NAC",
        "PAIS_NAC",
        "DEPARTA_RESI",
        "CIUDAD_RESI",
        "DIRECC_RESI",
        "TELEFONO",
        "E_MAIL",
        "NOMBRE_INSTITU",
        "OBSERVACIONES",
        "FOTO_DEPORTISTA",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("SEXO_DEPORTISTA")
    @classmethod
    def validate_sex(cls, value: str) -> str:
        value = value.upper()
        if value not in {"M", "F"}:
            raise ValueError("El sexo debe ser M o F")
        return value

    @field_validator("FECHA_NAC")
    @classmethod
    def validate_birth_date(cls, value: Optional[date]) -> Optional[date]:
        if value and value > date.today():
            raise ValueError("La fecha de nacimiento no puede estar en el futuro")
        return value


class DeportistaResponse(DeportistaCreate):
    model_config = ConfigDict(from_attributes=True)


class DeportistaPage(BaseModel):
    items: List[DeportistaResponse]
    total: int
    page: int
    page_size: int
