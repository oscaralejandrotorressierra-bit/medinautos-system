"""
Script para crear las tablas iniciales de la base de datos
"""

from backend.app.core.database import engine, Base
from backend.app.models.servicio import Servicio


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")


if __name__ == "__main__":
    crear_tablas()
