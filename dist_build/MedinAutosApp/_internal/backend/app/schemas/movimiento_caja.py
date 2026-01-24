"""
Schema de validacion para movimientos de caja
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MovimientoCajaCreateSchema(BaseModel):
    caja_id: Optional[int] = None
    tipo: str = Field(..., max_length=20)
    concepto: str = Field(..., max_length=120)
    monto: float = Field(..., gt=0)
    motivo: Optional[str] = Field(None, max_length=255)
    orden_id: Optional[int] = None
    proveedor_id: Optional[int] = None


class MovimientoCajaResponseSchema(BaseModel):
    id: int
    caja_id: int
    tipo: str
    concepto: str
    monto: float
    fecha: datetime
    motivo: Optional[str] = None
    usuario: Optional[str] = None
    orden_id: Optional[int] = None
    proveedor_id: Optional[int] = None

    class Config:
        from_attributes = True
