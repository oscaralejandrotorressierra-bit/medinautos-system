"""
Rutas del módulo de vehículos - MedinAutos

Este módulo gestiona:
- Listado de vehículos
- Creación de vehículos
- Edición de vehículos
- Eliminación de vehículos
- Asociación de vehículos con clientes

Todas las acciones redirigen con flags (?created, ?updated, ?deleted)
para ser capturadas por SweetAlert en el frontend.
"""

# ===============================
# IMPORTS FASTAPI
# ===============================
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates



# ===============================
# UTILIDADES
# ===============================
from starlette.status import HTTP_303_SEE_OTHER
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


# ===============================
# BASE DE DATOS Y MODELOS
# ===============================
from backend.app.core.database import get_db
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.cliente import Cliente

# ===============================
# CONFIGURACIÓN DEL ROUTER
# ===============================
router = APIRouter()
templates = Jinja2Templates(directory="backend/app/templates")

# ======================================================
# LISTAR VEHÍCULOS
# ======================================================

@router.get("/vehiculos", response_class=HTMLResponse)
def listar_vehiculos(request: Request, db: Session = Depends(get_db)):
    """
    Muestra el listado de vehículos registrados en el sistema.
    Incluye la relación con el cliente.
    """

    vehiculos = db.query(Vehiculo).all()

    return templates.TemplateResponse(
        "vehiculos/listar.html",
        {
            "request": request,
            "vehiculos": vehiculos
        }
    )

# ======================================================
# FORMULARIO CREAR VEHÍCULO (GET)
# ======================================================

@router.get("/vehiculos/crear", response_class=HTMLResponse)
def crear_vehiculo_form(request: Request, db: Session = Depends(get_db)):
    """
    Muestra el formulario para registrar un nuevo vehículo.
    Se cargan los clientes para asociarlo correctamente.
    """

    clientes = db.query(Cliente).all()

    return templates.TemplateResponse(
        "vehiculos/crear.html",
        {
            "request": request,
            "clientes": clientes
        }
    )

# ======================================================
# GUARDAR VEHÍCULO (POST)
# ======================================================

@router.post("/vehiculos/crear")
def crear_vehiculo(
    cliente_id: int = Form(...),
    placa: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    anio: int | None = Form(None),
    color: str | None = Form(None),
    db: Session = Depends(get_db)
):
    """
    Guarda un nuevo vehículo en la base de datos
    y lo asocia a un cliente existente.
    """

    vehiculo = Vehiculo(
        placa=placa.upper(),   # Normalizamos la placa
        marca=marca,
        modelo=modelo,
        anio=anio,
        color=color,
        cliente_id=cliente_id
    )

    db.add(vehiculo)
    db.add(vehiculo)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            "/vehiculos/crear?duplicate=1",
            status_code=HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        "/vehiculos?created=1",
        status_code=HTTP_303_SEE_OTHER
    )


# ======================================================
# FORMULARIO EDITAR VEHÍCULO (GET)
# ======================================================

@router.get("/vehiculos/{vehiculo_id}/editar", response_class=HTMLResponse)
def editar_vehiculo_form(
    vehiculo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Muestra el formulario para editar un vehículo existente.
    """

    vehiculo = db.query(Vehiculo).get(vehiculo_id)
    clientes = db.query(Cliente).all()

    if not vehiculo:
        return RedirectResponse(
            "/vehiculos",
            status_code=HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "vehiculos/editar.html",
        {
            "request": request,
            "vehiculo": vehiculo,
            "clientes": clientes
        }
    )

# ======================================================
# GUARDAR EDICIÓN VEHÍCULO (POST)
# ======================================================

@router.post("/vehiculos/{vehiculo_id}/editar")
def editar_vehiculo(
    vehiculo_id: int,
    placa: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    anio: int | None = Form(None),
    color: str | None = Form(None),
    cliente_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Guarda los cambios realizados a un vehículo.
    """

    vehiculo = db.query(Vehiculo).get(vehiculo_id)

    if not vehiculo:
        return RedirectResponse(
            "/vehiculos",
            status_code=HTTP_303_SEE_OTHER
        )

    vehiculo.placa = placa.upper()
    vehiculo.marca = marca
    vehiculo.modelo = modelo
    vehiculo.anio = anio
    vehiculo.color = color
    vehiculo.cliente_id = cliente_id

    db.commit()

    # Flag para SweetAlert de actualización
    return RedirectResponse(
        "/vehiculos?updated=1",
        status_code=HTTP_303_SEE_OTHER
    )

# ======================================================
# ELIMINAR VEHÍCULO
# ======================================================

@router.post("/vehiculos/{vehiculo_id}/eliminar")
def eliminar_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un vehículo del sistema.
    """

    vehiculo = db.query(Vehiculo).get(vehiculo_id)

    if vehiculo:
        db.delete(vehiculo)
        db.commit()

    # Flag para SweetAlert de eliminación
    return RedirectResponse(
        "/vehiculos?deleted=1",
        status_code=HTTP_303_SEE_OTHER
)

