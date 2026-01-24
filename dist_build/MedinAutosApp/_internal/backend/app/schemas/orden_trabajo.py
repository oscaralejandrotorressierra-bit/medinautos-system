from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrdenTrabajoBase(BaseModel):
    descripcion: str
    estado: Optional[str] = "abierta"
    total: Optional[float] = 0.0
    forma_pago: Optional[str] = None
    cliente_id: int
    vehiculo_id: int


class OrdenTrabajoCreate(OrdenTrabajoBase):
    pass


class OrdenTrabajoUpdate(BaseModel):
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    total: Optional[float] = None
    forma_pago: Optional[str] = None
    cliente_id: Optional[int] = None
    vehiculo_id: Optional[int] = None


class OrdenTrabajoResponse(OrdenTrabajoBase):
    id: int
    fecha: datetime
    fecha_reapertura: Optional[datetime] = None

    class Config:
        from_attributes = True
