from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"

    id = Column(Integer, primary_key=True, index=True)
    caja_id = Column(Integer, ForeignKey("cajas.id"), nullable=False)
    tipo = Column(String(20), nullable=False)
    concepto = Column(String(120), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String(255), nullable=True)
    usuario = Column(String(100), nullable=True)

    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)

    caja = relationship("Caja", back_populates="movimientos")
    orden = relationship("OrdenTrabajo")
    proveedor = relationship("Proveedor")
