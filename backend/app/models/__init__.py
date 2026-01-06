"""
Inicialización del paquete models.

Importa todos los modelos ORM para que SQLAlchemy
pueda registrarlos correctamente al iniciar la aplicación.
"""

from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
