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


class OrdenTrabajoUpdate(BaseModel):
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    total: Optional[float] = None
    cliente_id: Optional[int] = None
    vehiculo_id: Optional[int] = None


class OrdenTrabajoResponse(OrdenTrabajoBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
