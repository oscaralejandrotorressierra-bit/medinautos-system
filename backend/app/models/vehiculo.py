"""
Modelo Vehiculo - MedinAutos
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Vehiculo(Base):
    """
    Representa un vehículo registrado en el sistema.
    """

    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, nullable=False, unique=True, index=True)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    color = Column(String, nullable=True)
    anio = Column(Integer, nullable=True)
    cilindraje = Column(Integer, nullable=True)
    clase = Column(String, nullable=True)
    km_actual = Column(Integer, nullable=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # 🔥 RELACIÓN INVERSA (ESTO FALTABA)
    cliente = relationship(
        "Cliente",
        back_populates="vehiculos"
    )
