"""
Inicialización del paquete models.

Importa todos los modelos ORM para que SQLAlchemy
pueda registrarlos correctamente al iniciar la aplicación.
"""
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.servicio import Servicio
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
