"""
Schema de validación para Servicios
"""

from pydantic import BaseModel, Field
from typing import Optional


class ServicioBaseSchema(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre del servicio"
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=255,
        description="Descripción del servicio"
    )
    precio: float = Field(
        ...,
        gt=0,
        description="Precio del servicio (mayor que 0)"
    )
    categoria: Optional[str] = Field(
        None,
        max_length=50,
        description="Categoría del servicio"
    )


class ServicioCreateSchema(ServicioBaseSchema):
    pass


class ServicioUpdateSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool]


class ServicioResponseSchema(ServicioBaseSchema):
    id: int
    activo: bool

    class Config:
        from_attributes = True
