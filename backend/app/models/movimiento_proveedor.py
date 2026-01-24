from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class MovimientoProveedor(Base):
    __tablename__ = "movimientos_proveedor"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("almacen_items.id"), nullable=True)

    tipo = Column(String(20), nullable=False)
    cantidad = Column(Float, nullable=True)
    valor_unitario = Column(Float, nullable=True)
    subtotal = Column(Float, nullable=False)
    motivo = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100), nullable=True)

    proveedor = relationship("Proveedor", backref="movimientos")
    orden = relationship("OrdenTrabajo")
    item = relationship("AlmacenItem")
