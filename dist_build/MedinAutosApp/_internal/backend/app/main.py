"""
Main - MedinAutos
Punto de entrada principal de la aplicacion FastAPI.
"""

import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Templates
from backend.app.core.templates import templates

# Base de datos
from backend.app.core.database import engine
from sqlalchemy import text

# Modelos (IMPORTANTE para crear tablas)
from backend.app.models.usuario import Usuario
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.servicio import Servicio
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.models.mecanico import Mecanico
from backend.app.models.orden_mecanico import OrdenMecanico
from backend.app.models.proveedor import Proveedor
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.movimiento_almacen import MovimientoAlmacen
from backend.app.models.detalle_almacen import DetalleAlmacen
from backend.app.models.herramienta import Herramienta
from backend.app.models.prestamo_herramienta import PrestamoHerramienta
from backend.app.models.caja import Caja
from backend.app.models.movimiento_caja import MovimientoCaja
from backend.app.models.movimiento_proveedor import MovimientoProveedor
from backend.app.models.liquidacion_mecanico import LiquidacionMecanico
from backend.app.models.liquidacion_mecanico_detalle import LiquidacionMecanicoDetalle

from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.core.security import encriptar_password

# Rutas
from backend.app.routes import clientes
from backend.app.routes import frontend  # LOGIN + DASHBOARD + LOGOUT
from backend.app.routes import dashboard
from backend.app.routes import vehiculos
from backend.app.routes import servicios
from backend.app.routes import categorias_servicio
from backend.app.routes import ordenes_trabajo
from backend.app.routes import detalle_orden
from backend.app.routes import mecanicos
from backend.app.routes import almacen
from backend.app.routes import detalle_almacen
from backend.app.routes import herramientas
from backend.app.routes import contabilidad
from backend.app.routes import reportes
from backend.app.routes import reportes_export


def crear_admin_si_no_existe():
    """
    Crea un usuario administrador por defecto
    si la base de datos esta vacia.
    """
    db: Session = SessionLocal()
    try:
        admin = db.query(Usuario).filter(
            Usuario.username == "admin"
        ).first()

        if not admin:
            admin = Usuario(
                username="admin",
                password=encriptar_password("admin123"),
                rol="admin"
            )

            db.add(admin)
            db.commit()
    finally:
        db.close()

def asegurar_columnas():
    with engine.begin() as conn:
        resultado = conn.execute(text("PRAGMA table_info(ordenes_trabajo)"))
        columnas = {row[1] for row in resultado}
        if "forma_pago" not in columnas:
            conn.execute(text("ALTER TABLE ordenes_trabajo ADD COLUMN forma_pago VARCHAR(30)"))

# ============================================
# Crear aplicacion FastAPI
# ============================================

app = FastAPI(
    title="Sistema Taller MedinAutos",
    description="Sistema administrativo y operativo del taller MedinAutos",
    version="1.0.0"
)

# ============================================
# Crear tablas si no existen
# ============================================

Usuario.metadata.create_all(bind=engine)
Cliente.metadata.create_all(bind=engine)
Vehiculo.metadata.create_all(bind=engine)
Servicio.metadata.create_all(bind=engine)
CategoriaServicio.metadata.create_all(bind=engine)
OrdenTrabajo.metadata.create_all(bind=engine)
DetalleOrden.metadata.create_all(bind=engine)
Mecanico.metadata.create_all(bind=engine)
OrdenMecanico.metadata.create_all(bind=engine)
Proveedor.metadata.create_all(bind=engine)
AlmacenItem.metadata.create_all(bind=engine)
MovimientoAlmacen.metadata.create_all(bind=engine)
DetalleAlmacen.metadata.create_all(bind=engine)
Herramienta.metadata.create_all(bind=engine)
PrestamoHerramienta.metadata.create_all(bind=engine)
Caja.metadata.create_all(bind=engine)
MovimientoCaja.metadata.create_all(bind=engine)
MovimientoProveedor.metadata.create_all(bind=engine)
LiquidacionMecanico.metadata.create_all(bind=engine)
LiquidacionMecanicoDetalle.metadata.create_all(bind=engine)

asegurar_columnas()
crear_admin_si_no_existe()


# ============================================
# Archivos estaticos
# ============================================

def _base_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "backend", "app")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))


app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_base_app_dir(), "static")),
    name="static"
)

# ============================================
# HOME (REDIRECCION AL LOGIN)
# ============================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# ============================================
# REGISTRO DE ROUTERS
# ============================================

app.include_router(frontend.router)   # LOGIN / DASHBOARD / LOGOUT
app.include_router(clientes.router)   # CRUD CLIENTES
app.include_router(dashboard.router)  # DATOS DEL DASHBOARD
app.include_router(vehiculos.router)  # CRUD VEHICULOS
app.include_router(servicios.router, prefix="/api")
app.include_router(categorias_servicio.router, prefix="/api")
app.include_router(ordenes_trabajo.router, prefix="/api")
app.include_router(detalle_orden.router, prefix="/api")
app.include_router(mecanicos.router, prefix="/api")
app.include_router(almacen.router, prefix="/api")
app.include_router(detalle_almacen.router, prefix="/api")
app.include_router(herramientas.router, prefix="/api")
app.include_router(contabilidad.router, prefix="/api")
app.include_router(reportes.router, prefix="/api")
app.include_router(reportes_export.router, prefix="/api")


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    return {"status": "ok"}
