from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.core.database import Base


class OrdenMecanico(Base):
    __tablename__ = "ordenes_mecanicos"
    __table_args__ = (
        UniqueConstraint("orden_id", "mecanico_id", name="uq_orden_mecanico"),
    )

    id = Column(Integer, primary_key=True, index=True)

    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)
    mecanico_id = Column(Integer, ForeignKey("mecanicos.id"), nullable=False)

    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    observaciones = Column(String(255), nullable=True)

    orden = relationship("OrdenTrabajo", back_populates="asignaciones_mecanicos")
    mecanico = relationship("Mecanico", back_populates="asignaciones_ordenes")

    def __repr__(self):
        return f"<OrdenMecanico orden={self.orden_id} mecanico={self.mecanico_id}>"
