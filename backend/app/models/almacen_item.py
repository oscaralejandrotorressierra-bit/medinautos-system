from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class AlmacenItem(Base):
    __tablename__ = "almacen_items"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)
    categoria = Column(String(80), nullable=True)
    unidad = Column(String(20), nullable=False, default="unidad")

    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)

    valor_proveedor = Column(Float, default=0.0)
    valor_taller = Column(Float, default=0.0)

    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    proveedor = relationship("Proveedor", backref="insumos")

    def __repr__(self):
        return f"<AlmacenItem {self.nombre}>"
