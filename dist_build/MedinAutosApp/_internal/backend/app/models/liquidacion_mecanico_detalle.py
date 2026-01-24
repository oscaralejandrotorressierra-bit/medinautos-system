from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class LiquidacionMecanicoDetalle(Base):
    __tablename__ = "liquidaciones_mecanicos_detalle"

    id = Column(Integer, primary_key=True, index=True)
    liquidacion_id = Column(Integer, ForeignKey("liquidaciones_mecanicos.id"), nullable=False)
    orden_id = Column(Integer, ForeignKey("ordenes_trabajo.id"), nullable=False)
    porcentaje = Column(Float, nullable=False, default=0.0)
    base_calculo = Column(Float, nullable=False, default=0.0)
    monto = Column(Float, nullable=False, default=0.0)

    liquidacion = relationship("LiquidacionMecanico", back_populates="detalles")
    orden = relationship("OrdenTrabajo")
