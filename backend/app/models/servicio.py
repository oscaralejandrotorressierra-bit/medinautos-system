from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from backend.app.core.database import Base


class Servicio(Base):
    __tablename__ = "servicios"

    # Identificador
    id = Column(Integer, primary_key=True, index=True)

    # Información básica
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    # Precio del servicio
    precio = Column(Float, nullable=False)

    # Clasificación del servicio
    categoria = Column(String(50), nullable=True)

    # Estado (activo / inactivo)
    activo = Column(Boolean, default=True)

    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Servicio {self.nombre}>"