"""
Main - MedinAutos
Punto de entrada principal de la aplicación FastAPI.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Templates
from backend.app.core.templates import templates

# Base de datos
from backend.app.core.database import engine

# Modelos (IMPORTANTE para crear tablas)
from backend.app.models.usuario import Usuario
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.core.security import encriptar_password




# Rutas
# Rutas
from backend.app.routes import clientes
from backend.app.routes import frontend  # LOGIN + DASHBOARD + LOGOUT
from backend.app.routes import dashboard
from backend.app.routes import vehiculos


def crear_admin_si_no_existe():
    """
    Crea un usuario administrador por defecto
    si la base de datos está vacía.
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

# ============================================
# Crear aplicación FastAPI
# ============================================

app = FastAPI(
    title="Sistema Taller MedinAutos",
    description="Sistema administrativo y operativo del taller MedinAutos",
    version="1.0.0"
)

# ============================================
# Crear tablas si no existen
# (ESTE ERA EL FALTANTE 🔥)
# ============================================

Usuario.metadata.create_all(bind=engine)
Cliente.metadata.create_all(bind=engine)
Vehiculo.metadata.create_all(bind=engine)

crear_admin_si_no_existe()


# ============================================
# Archivos estáticos
# ============================================

app.mount(
    "/static",
    StaticFiles(directory="backend/app/static"),
    name="static"
)

# ============================================
# HOME (REDIRECCIÓN AL LOGIN)
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
app.include_router(vehiculos.router)


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    return {"status": "ok"}
