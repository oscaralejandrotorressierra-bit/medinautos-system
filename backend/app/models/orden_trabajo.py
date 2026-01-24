from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base





class OrdenTrabajo(Base):
    __tablename__ = "ordenes_trabajo"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    fecha_reapertura = Column(DateTime, nullable=True)
    fecha_salida = Column(DateTime, nullable=True)
    descripcion = Column(String(255), nullable=False)
    estado = Column(String(20), default="abierta")
    total = Column(Float, default=0.0)
    forma_pago = Column(String(30), nullable=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)

    cliente = relationship("Cliente", backref="ordenes")
    vehiculo = relationship("Vehiculo", backref="ordenes")

    asignaciones_mecanicos = relationship(
        "OrdenMecanico",
        back_populates="orden",
        cascade="all, delete-orphan"
    )
