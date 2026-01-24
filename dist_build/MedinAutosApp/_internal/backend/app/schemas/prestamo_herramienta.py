"""
Schema de validacion para prestamos de herramientas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PrestamoHerramientaCreateSchema(BaseModel):
    herramienta_id: int
    mecanico_id: int
    observaciones: Optional[str] = Field(None, max_length=255)


class PrestamoHerramientaDevolucionSchema(BaseModel):
    observaciones: Optional[str] = Field(None, max_length=255)


class PrestamoHerramientaResponseSchema(BaseModel):
    id: int
    herramienta_id: int
    mecanico_id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True
