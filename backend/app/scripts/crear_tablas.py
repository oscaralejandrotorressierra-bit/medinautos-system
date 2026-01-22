"""
Script para crear las tablas iniciales de la base de datos
"""

from backend.app.core.database import engine, Base
from backend.app.models.servicio import Servicio
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")


if __name__ == "__main__":
    crear_tablas()
