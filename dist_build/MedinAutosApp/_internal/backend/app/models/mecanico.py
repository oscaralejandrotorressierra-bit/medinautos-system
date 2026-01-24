from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Mecanico(Base):
    __tablename__ = "mecanicos"

    id = Column(Integer, primary_key=True, index=True)

    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    documento = Column(String(50), nullable=False, unique=True)

    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    especialidad = Column(String(80), nullable=True)

    fecha_ingreso = Column(Date, nullable=True)
    activo = Column(Boolean, default=True)
    porcentaje_base = Column(Float, default=0.0)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    asignaciones_ordenes = relationship(
        "OrdenMecanico",
        back_populates="mecanico",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Mecanico {self.documento}>"
