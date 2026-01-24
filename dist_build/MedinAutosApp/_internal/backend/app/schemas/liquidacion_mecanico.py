"""
Schema de validacion para liquidaciones de mecanicos
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class LiquidacionMecanicoCreateSchema(BaseModel):
    mecanico_id: int
    fecha_inicio: date
    fecha_fin: date
    frecuencia: str = Field(..., max_length=20)
    observaciones: Optional[str] = Field(None, max_length=255)


class LiquidacionMecanicoDetalleSchema(BaseModel):
    id: int
    orden_id: int
    porcentaje: float
    base_calculo: float
    monto: float

    class Config:
        from_attributes = True


class LiquidacionMecanicoResponseSchema(BaseModel):
    id: int
    mecanico_id: int
    fecha_inicio: date
    fecha_fin: date
    frecuencia: str
    total_base: float
    total_pagado: float
    estado: str
    fecha_creacion: datetime
    usuario: Optional[str] = None
    observaciones: Optional[str] = None
    detalles: list[LiquidacionMecanicoDetalleSchema] = []

    class Config:
        from_attributes = True
