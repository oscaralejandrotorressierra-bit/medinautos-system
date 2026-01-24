"""
Schema de validacion para movimientos de almacen
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class MovimientoAlmacenResponseSchema(BaseModel):
    """Schema de respuesta para movimientos."""

    id: int
    tipo: str
    cantidad: float
    valor_unitario: Optional[float] = None
    observaciones: Optional[str] = None
    fecha: datetime
    item_id: int
    proveedor_id: Optional[int] = None
    orden_id: Optional[int] = None

    class Config:
        """Config de Pydantic para mapeo ORM."""

        from_attributes = True
