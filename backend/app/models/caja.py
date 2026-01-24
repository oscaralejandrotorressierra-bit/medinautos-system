from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Caja(Base):
    __tablename__ = "cajas"

    id = Column(Integer, primary_key=True, index=True)
    fecha_apertura = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    saldo_inicial = Column(Float, default=0.0)
    saldo_final = Column(Float, default=0.0)
    estado = Column(String(20), default="abierta")
    observaciones = Column(String(255), nullable=True)
    usuario_apertura = Column(String(100), nullable=True)
    usuario_cierre = Column(String(100), nullable=True)

    movimientos = relationship(
        "MovimientoCaja",
        back_populates="caja",
        cascade="all, delete-orphan"
    )
