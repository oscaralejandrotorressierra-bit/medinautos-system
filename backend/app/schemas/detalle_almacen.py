"""
Schema de validacion para insumos en ordenes
"""

from pydantic import BaseModel


class DetalleAlmacenCreate(BaseModel):
    orden_id: int
    item_id: int
    cantidad: float


class DetalleAlmacenResponse(BaseModel):
    id: int
    orden_id: int
    item_id: int
    cantidad: float
    precio_unitario: float
    subtotal: float

    class Config:
        orm_mode = True
