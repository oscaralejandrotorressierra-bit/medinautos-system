"""
Schema de validacion para insumos de almacen
"""

from typing import Optional

from pydantic import BaseModel, Field


class AlmacenItemBaseSchema(BaseModel):
    """Base schema para insumos."""

    nombre: str = Field(..., min_length=2, max_length=120)
    descripcion: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=80)
    unidad: str = Field("unidad", max_length=20)
    stock_actual: float = Field(0, ge=0)
    stock_minimo: float = Field(0, ge=0)
    valor_proveedor: float = Field(0, ge=0)
    valor_taller: float = Field(0, ge=0)
    proveedor_id: Optional[int] = None


class AlmacenItemCreateSchema(AlmacenItemBaseSchema):
    """Schema de creacion para insumos."""


class AlmacenItemUpdateSchema(BaseModel):
    """Schema de actualizacion para insumos."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    descripcion: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=80)
    unidad: Optional[str] = Field(None, max_length=20)
    stock_actual: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[float] = Field(None, ge=0)
    valor_proveedor: Optional[float] = Field(None, ge=0)
    valor_taller: Optional[float] = Field(None, ge=0)
    proveedor_id: Optional[int] = None
    activo: Optional[bool] = None


class AlmacenItemResponseSchema(AlmacenItemBaseSchema):
    """Schema de respuesta para insumos."""

    id: int
    activo: bool

    class Config:
        """Config de Pydantic para mapeo ORM."""

        from_attributes = True


class MovimientoEntradaSchema(BaseModel):
    """Schema para registrar entradas de stock."""

    cantidad: float = Field(..., gt=0)
    valor_unitario: Optional[float] = Field(None, ge=0)
    proveedor_id: Optional[int] = None
    observaciones: Optional[str] = Field(None, max_length=255)
