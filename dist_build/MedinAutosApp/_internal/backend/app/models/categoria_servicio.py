from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from backend.app.core.database import Base


class CategoriaServicio(Base):
    __tablename__ = "categorias_servicio"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(80), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CategoriaServicio {self.nombre}>"
