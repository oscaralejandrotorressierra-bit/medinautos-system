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
    proveedor_id: int | None
    cantidad: float
    precio_unitario: float
    subtotal: float
    costo_proveedor_unitario: float
    subtotal_proveedor: float
    margen_subtotal: float

    class Config:
        from_attributes = True
