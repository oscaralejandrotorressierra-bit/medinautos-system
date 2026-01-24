"""
Modelo VehiculoRecomendacion - MedinAutos
Estado por vehiculo para cada regla de mantenimiento.
"""

from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class VehiculoRecomendacion(Base):
    __tablename__ = "vehiculos_recomendaciones"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    regla_id = Column(Integer, ForeignKey("recomendaciones_reglas.id"), nullable=False)
    km_base = Column(Integer, nullable=True)
    fecha_base = Column(Date, nullable=True)

    vehiculo = relationship("Vehiculo")
    regla = relationship("RecomendacionRegla")
