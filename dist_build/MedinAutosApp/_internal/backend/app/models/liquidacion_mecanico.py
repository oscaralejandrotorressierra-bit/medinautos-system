from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class LiquidacionMecanico(Base):
    __tablename__ = "liquidaciones_mecanicos"

    id = Column(Integer, primary_key=True, index=True)
    mecanico_id = Column(Integer, ForeignKey("mecanicos.id"), nullable=False)

    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    frecuencia = Column(String(20), nullable=False)

    total_base = Column(Float, default=0.0)
    total_pagado = Column(Float, default=0.0)
    estado = Column(String(20), default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100), nullable=True)
    observaciones = Column(String(255), nullable=True)

    mecanico = relationship("Mecanico")
    detalles = relationship(
        "LiquidacionMecanicoDetalle",
        back_populates="liquidacion",
        cascade="all, delete-orphan"
    )
