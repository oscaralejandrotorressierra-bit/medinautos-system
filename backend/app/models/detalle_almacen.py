from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class DetalleAlmacen(Base):
    __tablename__ = "detalle_almacen"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("almacen_items.id"), nullable=False)

    cantidad = Column(Float, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    orden = relationship("OrdenTrabajo", backref="insumos")
    item = relationship("AlmacenItem")
