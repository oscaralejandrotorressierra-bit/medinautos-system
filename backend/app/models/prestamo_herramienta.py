from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class PrestamoHerramienta(Base):
    __tablename__ = "prestamos_herramienta"

    id = Column(Integer, primary_key=True, index=True)
    herramienta_id = Column(Integer, ForeignKey("herramientas.id"), nullable=False)
    mecanico_id = Column(Integer, ForeignKey("mecanicos.id"), nullable=False)

    fecha_prestamo = Column(DateTime, default=datetime.utcnow)
    fecha_devolucion = Column(DateTime, nullable=True)
    observaciones = Column(String(255), nullable=True)

    herramienta = relationship("Herramienta", backref="prestamos")
    mecanico = relationship("Mecanico", backref="prestamos_herramientas")

    def __repr__(self):
        return f"<PrestamoHerramienta herramienta={self.herramienta_id}>"
