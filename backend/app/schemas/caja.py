"""
Schema de validacion para Caja
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CajaCreateSchema(BaseModel):
    saldo_inicial: float = Field(0.0, ge=0)
    observaciones: Optional[str] = Field(None, max_length=255)


class CajaCloseSchema(BaseModel):
    saldo_final: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = Field(None, max_length=255)


class CajaResponseSchema(BaseModel):
    id: int
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime] = None
    saldo_inicial: float
    saldo_final: float
    estado: str
    observaciones: Optional[str] = None
    usuario_apertura: Optional[str] = None
    usuario_cierre: Optional[str] = None

    class Config:
        from_attributes = True
