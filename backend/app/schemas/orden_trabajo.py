from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrdenTrabajoBase(BaseModel):
    descripcion: str
    estado: Optional[str] = "abierta"
    total: Optional[float] = 0.0
    cliente_id: int
    vehiculo_id: int


class OrdenTrabajoCreate(OrdenTrabajoBase):
    pass


class OrdenTrabajoResponse(OrdenTrabajoBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
