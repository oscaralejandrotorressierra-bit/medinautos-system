from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from backend.app.core.database import Base





class DetalleOrden(Base):
    __tablename__ = "detalle_orden"

    id = Column(Integer, primary_key=True, index=True)

    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)

    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    orden = relationship("OrdenTrabajo", backref="detalles")
    servicio = relationship("Servicio")
