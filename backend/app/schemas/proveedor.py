"""
Schema de validacion para proveedores
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProveedorBaseSchema(BaseModel):
    """Base schema para proveedores."""

    nombre: str = Field(..., min_length=2, max_length=120)
    nit: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    direccion: Optional[str] = Field(None, max_length=150)


class ProveedorCreateSchema(ProveedorBaseSchema):
    """Schema de creacion para proveedores."""


class ProveedorUpdateSchema(BaseModel):
    """Schema de actualizacion para proveedores."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    nit: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    direccion: Optional[str] = Field(None, max_length=150)
    activo: Optional[bool] = None


class ProveedorResponseSchema(ProveedorBaseSchema):
    """Schema de respuesta para proveedores."""

    id: int
    activo: bool

    class Config:
        """Config de Pydantic para mapeo ORM."""

        from_attributes = True
