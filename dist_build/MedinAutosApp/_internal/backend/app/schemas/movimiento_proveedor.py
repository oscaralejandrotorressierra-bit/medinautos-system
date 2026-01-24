"""
Schema de validacion para movimientos de proveedores
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MovimientoProveedorCreateSchema(BaseModel):
    proveedor_id: int
    tipo: str = Field(..., max_length=20)
    subtotal: float = Field(..., gt=0)
    cantidad: Optional[float] = None
    valor_unitario: Optional[float] = None
    motivo: Optional[str] = Field(None, max_length=255)
    orden_id: Optional[int] = None
    item_id: Optional[int] = None


class MovimientoProveedorResponseSchema(BaseModel):
    id: int
    proveedor_id: int
    orden_id: Optional[int] = None
    item_id: Optional[int] = None
    tipo: str
    cantidad: Optional[float] = None
    valor_unitario: Optional[float] = None
    subtotal: float
    motivo: Optional[str] = None
    fecha: datetime
    usuario: Optional[str] = None

    class Config:
        from_attributes = True
