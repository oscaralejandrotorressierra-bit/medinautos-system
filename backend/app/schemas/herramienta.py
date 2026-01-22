"""
Schema de validacion para herramientas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class HerramientaBaseSchema(BaseModel):
    """Base schema para herramientas."""

    nombre: str = Field(..., min_length=2, max_length=120)
    codigo: str = Field(..., min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    ubicacion: Optional[str] = Field(None, max_length=120)
    valor: float = Field(0, ge=0)
    estado: Optional[str] = Field("disponible", max_length=30)


class HerramientaCreateSchema(HerramientaBaseSchema):
    """Schema de creacion para herramientas."""


class HerramientaUpdateSchema(BaseModel):
    """Schema de actualizacion para herramientas."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    codigo: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    ubicacion: Optional[str] = Field(None, max_length=120)
    valor: Optional[float] = Field(None, ge=0)
    estado: Optional[str] = Field(None, max_length=30)
    activo: Optional[bool] = None


class HerramientaResponseSchema(HerramientaBaseSchema):
    """Schema de respuesta para herramientas."""

    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        """Config de Pydantic para mapeo ORM."""

        from_attributes = True
