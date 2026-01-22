"""
Schema de validacion para categorias de servicio
"""

from typing import Optional

from pydantic import BaseModel, Field

class CategoriaServicioBaseSchema(BaseModel):
    """Base schema para categorias de servicio."""
    nombre: str = Field(..., min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)


class CategoriaServicioCreateSchema(CategoriaServicioBaseSchema):
    """Schema de creacion para categorias de servicio."""
    activo: Optional[bool] = True


class CategoriaServicioUpdateSchema(BaseModel):
    """Schema de actualizacion para categorias de servicio."""
    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool]


class CategoriaServicioResponseSchema(CategoriaServicioBaseSchema):
    """Schema de respuesta para categorias de servicio."""
    id: int
    activo: bool

    class Config:
        """Config de Pydantic para mapeo ORM."""
        from_attributes = True
