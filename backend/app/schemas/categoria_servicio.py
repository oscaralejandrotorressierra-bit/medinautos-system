"""
Schema de validacion para categorias de servicio
"""

from pydantic import BaseModel, Field
from typing import Optional


class CategoriaServicioBaseSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)


class CategoriaServicioCreateSchema(CategoriaServicioBaseSchema):
    activo: Optional[bool] = True


class CategoriaServicioUpdateSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool]


class CategoriaServicioResponseSchema(CategoriaServicioBaseSchema):
    id: int
    activo: bool

    class Config:
        from_attributes = True
