"""
Modelo RecomendacionRegla - MedinAutos
Reglas globales de mantenimiento por km y/o tiempo.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class RecomendacionRegla(Base):
    __tablename__ = "recomendaciones_reglas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)
    intervalo_km = Column(Integer, nullable=True)
    intervalo_dias = Column(Integer, nullable=True)
    tolerancia_km = Column(Integer, nullable=False, default=200)
    tolerancia_dias = Column(Integer, nullable=False, default=3)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
