from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class MovimientoAlmacen(Base):
    __tablename__ = "movimientos_almacen"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    cantidad = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=True)
    observaciones = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    item_id = Column(Integer, ForeignKey("almacen_items.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=True)

    item = relationship("AlmacenItem")
    proveedor = relationship("Proveedor")
    orden = relationship("OrdenTrabajo")

    def __repr__(self):
        return f"<MovimientoAlmacen {self.tipo} {self.cantidad}>"
