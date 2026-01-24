"""
Modelo Cliente - MedinAutos
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Cliente(Base):
    """
    Representa un cliente del taller.

    Un cliente puede tener uno o varios vehículos asociados.
    """

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    documento = Column(String, nullable=False, unique=True)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Relación con vehículos
    vehiculos = relationship(
        "Vehiculo",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )
