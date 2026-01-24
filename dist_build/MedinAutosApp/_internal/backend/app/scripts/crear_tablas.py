"""
Script para crear las tablas iniciales de la base de datos
"""

from backend.app.core.database import engine, Base
from backend.app.models.servicio import Servicio
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.models.mecanico import Mecanico
from backend.app.models.orden_mecanico import OrdenMecanico
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.detalle_almacen import DetalleAlmacen
from backend.app.models.movimiento_almacen import MovimientoAlmacen
from backend.app.models.proveedor import Proveedor
from backend.app.models.caja import Caja
from backend.app.models.movimiento_caja import MovimientoCaja
from backend.app.models.movimiento_proveedor import MovimientoProveedor
from backend.app.models.liquidacion_mecanico import LiquidacionMecanico
from backend.app.models.liquidacion_mecanico_detalle import LiquidacionMecanicoDetalle


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")


if __name__ == "__main__":
    crear_tablas()
