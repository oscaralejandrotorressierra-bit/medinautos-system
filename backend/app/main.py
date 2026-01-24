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
from backend.app.models.recomendacion_regla import RecomendacionRegla
from backend.app.models.vehiculo_recomendacion import VehiculoRecomendacion

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
from backend.app.routes import novedades


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
        if "fecha_salida" not in columnas:
            conn.execute(text("ALTER TABLE ordenes_trabajo ADD COLUMN fecha_salida DATETIME"))


def asegurar_reglas_novedades():
    reglas_base = [
        {"nombre": "Cambio de aceite", "descripcion": "Aceite de motor y filtro", "km": 5000, "dias": 180},
        {"nombre": "Filtro de aire", "descripcion": "Filtro de aire del motor", "km": 10000, "dias": 365},
        {"nombre": "Filtro de cabina", "descripcion": "Filtro de habitaculo", "km": 10000, "dias": 365},
        {"nombre": "Filtro de combustible", "descripcion": "Filtro de combustible", "km": 20000, "dias": 365},
        {"nombre": "Liquido de frenos", "descripcion": "Cambio de liquido de frenos", "km": 20000, "dias": 365},
        {"nombre": "Refrigerante", "descripcion": "Cambio de refrigerante", "km": 40000, "dias": 730},
        {"nombre": "Correa de reparticion", "descripcion": "Kit de distribucion", "km": 60000, "dias": 1460},
        {"nombre": "Correa de accesorios", "descripcion": "Revision correa accesorios", "km": 40000, "dias": 1095},
        {"nombre": "Bujias", "descripcion": "Cambio de bujias", "km": 30000, "dias": 730},
        {"nombre": "Alineacion", "descripcion": "Alineacion y geometria", "km": 10000, "dias": 365},
        {"nombre": "Balanceo", "descripcion": "Balanceo de ruedas", "km": 10000, "dias": 365},
        {"nombre": "Rotacion llantas", "descripcion": "Rotacion de llantas", "km": 10000, "dias": 365},
        {"nombre": "Revision frenos", "descripcion": "Pastillas y discos", "km": 15000, "dias": 365},
        {"nombre": "Suspension", "descripcion": "Revision suspension", "km": 20000, "dias": 365},
        {"nombre": "Bateria", "descripcion": "Revision bateria", "km": 40000, "dias": 730},
        {"nombre": "Amortiguadores", "descripcion": "Revision amortiguadores", "km": 30000, "dias": 730},
        {"nombre": "Bujes", "descripcion": "Revision bujes de suspension", "km": 30000, "dias": 730},
        {"nombre": "Direccion", "descripcion": "Revision de direccion", "km": 20000, "dias": 365},
        {"nombre": "Aceite de caja", "descripcion": "Cambio de aceite de caja", "km": 40000, "dias": 730},
        {"nombre": "Embrague", "descripcion": "Revision de embrague", "km": 50000, "dias": 1095},
        {"nombre": "Inyectores", "descripcion": "Limpieza de inyectores", "km": 30000, "dias": 365},
        {"nombre": "Cuerpo de aceleracion", "descripcion": "Limpieza cuerpo de aceleracion", "km": 25000, "dias": 365},
        {"nombre": "Sistema de escape", "descripcion": "Revision de escape", "km": 30000, "dias": 365},
        {"nombre": "Luces", "descripcion": "Revision de luces", "km": 10000, "dias": 180},
        {"nombre": "Escaneo", "descripcion": "Escaneo preventivo", "km": 20000, "dias": 365},
        {"nombre": "Frenos de mano", "descripcion": "Ajuste freno de mano", "km": 20000, "dias": 365},
        {"nombre": "Presion de llantas", "descripcion": "Revision presion de llantas", "km": 5000, "dias": 90},
    ]

    db: Session = SessionLocal()
    try:
        existentes = {r.nombre for r in db.query(RecomendacionRegla).all()}
        for regla in reglas_base:
            if regla["nombre"] in existentes:
                continue
            db.add(RecomendacionRegla(
                nombre=regla["nombre"],
                descripcion=regla["descripcion"],
                intervalo_km=regla["km"],
                intervalo_dias=regla["dias"],
                tolerancia_km=200,
                tolerancia_dias=3,
                activo=True
            ))
        db.commit()
    finally:
        db.close()

# ============================================
# Crear aplicacion FastAPI
# ============================================

app = FastAPI(
    title="Sistema Taller MedinAutos",
    description="Sistema administrativo y operativo del taller MedinAutos",
    version="1.1.0"
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
RecomendacionRegla.metadata.create_all(bind=engine)
VehiculoRecomendacion.metadata.create_all(bind=engine)

asegurar_columnas()
crear_admin_si_no_existe()
asegurar_reglas_novedades()


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
app.include_router(novedades.router)


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    return {"status": "ok"}
