from pydantic import BaseModel
from typing import Optional


class DetalleOrdenBase(BaseModel):
    orden_id: int
    servicio_id: int
    cantidad: int = 1


class DetalleOrdenCreate(DetalleOrdenBase):
    pass


class DetalleOrdenResponse(DetalleOrdenBase):
    id: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True
