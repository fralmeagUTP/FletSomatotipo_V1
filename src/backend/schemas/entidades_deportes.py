from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EntidadBase(BaseModel):
    NIT_ENTIDAD: str = Field(min_length=1, max_length=20)
    RAZON_SOCIAL: str = Field(min_length=1, max_length=50)
    TELEFONO: Optional[str] = Field(default=None, max_length=20)
    CONTACTO: Optional[str] = Field(default=None, max_length=50)
    E_MAIL: Optional[EmailStr] = None

    @field_validator("NIT_ENTIDAD", "RAZON_SOCIAL")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value

    @field_validator("TELEFONO", "CONTACTO", "E_MAIL", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class EntidadCreate(EntidadBase):
    pass


class EntidadResponse(EntidadBase):
    model_config = ConfigDict(from_attributes=True)


class EntidadPage(BaseModel):
    items: List[EntidadResponse]
    total: int
    page: int
    page_size: int


class DeporteBase(BaseModel):
    DEPORTE: str = Field(min_length=1, max_length=50)

    @field_validator("DEPORTE")
    @classmethod
    def strip_deporte(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value


class DeporteCreate(DeporteBase):
    ID_DEPORTE: Optional[int] = Field(default=None, gt=0)


class DeporteResponse(DeporteBase):
    model_config = ConfigDict(from_attributes=True)

    ID_DEPORTE: int


class DeportePage(BaseModel):
    items: List[DeporteResponse]
    total: int
    page: int
    page_size: int


class DeporteDeportistaBase(BaseModel):
    ID_DEPORTE: int = Field(gt=0)
    IDENTI_DEPORTISTA: str = Field(min_length=1, max_length=20)
    NIT_ENTIDAD: str = Field(min_length=1, max_length=20)

    @field_validator("IDENTI_DEPORTISTA", "NIT_ENTIDAD")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obligatorio")
        return value


class DeporteDeportistaCreate(DeporteDeportistaBase):
    pass


class DeporteDeportistaResponse(DeporteDeportistaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DeporteDeportistaPage(BaseModel):
    items: List[DeporteDeportistaResponse]
    total: int
    page: int
    page_size: int
