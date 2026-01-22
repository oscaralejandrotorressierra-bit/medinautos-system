from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from backend.app.core.database import Base


class Herramienta(Base):
    __tablename__ = "herramientas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    codigo = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    ubicacion = Column(String(120), nullable=True)
    valor = Column(Float, default=0.0)
    estado = Column(String(30), default="disponible")
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Herramienta {self.codigo}>"
