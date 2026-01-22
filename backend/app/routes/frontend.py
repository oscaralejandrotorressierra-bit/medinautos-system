"""
Rutas Frontend - Autenticación y Vistas
Sistema MedinAutos
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from backend.app.core.database import get_db
from backend.app.models.usuario import Usuario
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
from backend.app.core.security import (
    verificar_password,
    crear_token
)

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="backend/app/templates")


# =====================================
# LOGIN (FORMULARIO)
# =====================================
@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


# =====================================
# LOGIN (PROCESO)
# =====================================
@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.username == username
    ).first()

    if not usuario or not verificar_password(password, usuario.password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Usuario o contraseña incorrectos"
            }
        )

    token = crear_token({
        "sub": usuario.username,
        "rol": usuario.rol
    })

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True)

    return response


# =====================================
# SERVICIOS - LISTAR (FRONTEND)
# =====================================
@router.get("/servicios", response_class=HTMLResponse)
def vista_servicios(request: Request):
    return templates.TemplateResponse(
        "servicios/listar.html",
        {"request": request}
    )
# =====================================
# SERVICIOS - NUEVO (FORMULARIO)
# =====================================
@router.get("/servicios/nuevo", response_class=HTMLResponse)
def vista_nuevo_servicio(request: Request):
    return templates.TemplateResponse(
        "servicios/nuevo.html",
        {"request": request}
    )

@router.get("/mecanicos", response_class=HTMLResponse)
def vista_mecanicos(request: Request):
    return templates.TemplateResponse(
        "mecanicos/listar.html",
        {"request": request}
    )

@router.get("/mecanicos/nuevo", response_class=HTMLResponse)
def vista_nuevo_mecanico(request: Request):
    return templates.TemplateResponse(
        "mecanicos/nuevo.html",
        {"request": request}
    )

@router.get("/mecanicos/{mecanico_id}/editar", response_class=HTMLResponse)
def vista_editar_mecanico(request: Request, mecanico_id: int):
    return templates.TemplateResponse(
        "mecanicos/editar.html",
        {
            "request": request,
            "mecanico_id": mecanico_id
        }
    )

@router.get("/almacen", response_class=HTMLResponse)
def vista_almacen(request: Request):
    return templates.TemplateResponse(
        "almacen/listar.html",
        {"request": request}
    )

@router.get("/almacen/nuevo", response_class=HTMLResponse)
def vista_nuevo_insumo(request: Request):
    return templates.TemplateResponse(
        "almacen/nuevo.html",
        {"request": request}
    )

@router.get("/almacen/{item_id}/editar", response_class=HTMLResponse)
def vista_editar_insumo(request: Request, item_id: int):
    return templates.TemplateResponse(
        "almacen/editar.html",
        {"request": request, "item_id": item_id}
    )

@router.get("/almacen/proveedores", response_class=HTMLResponse)
def vista_proveedores(request: Request):
    return templates.TemplateResponse(
        "almacen/proveedores.html",
        {"request": request}
    )

@router.get("/herramientas", response_class=HTMLResponse)
def vista_herramientas(request: Request):
    return templates.TemplateResponse(
        "herramientas/listar.html",
        {"request": request}
    )

@router.get("/herramientas/nuevo", response_class=HTMLResponse)
def vista_nueva_herramienta(request: Request):
    return templates.TemplateResponse(
        "herramientas/nuevo.html",
        {"request": request}
    )

@router.get("/herramientas/{herramienta_id}/editar", response_class=HTMLResponse)
def vista_editar_herramienta(request: Request, herramienta_id: int):
    return templates.TemplateResponse(
        "herramientas/editar.html",
        {"request": request, "herramienta_id": herramienta_id}
    )

@router.get("/herramientas/prestamos", response_class=HTMLResponse)
def vista_prestamos_herramientas(request: Request):
    return templates.TemplateResponse(
        "herramientas/prestamos.html",
        {"request": request}
    )

@router.get("/ordenes", response_class=HTMLResponse)
def vista_ordenes(request: Request, db: Session = Depends(get_db)):
    ordenes = db.query(OrdenTrabajo).order_by(OrdenTrabajo.id.desc()).all()
    return templates.TemplateResponse(
        "ordenes/listar.html",
        {
            "request": request,
            "ordenes": ordenes
        }
    )

@router.get("/ordenes/nuevo", response_class=HTMLResponse)
def vista_nueva_orden(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).order_by(Cliente.nombre.asc()).all()
    vehiculos = db.query(Vehiculo).order_by(Vehiculo.placa.asc()).all()
    return templates.TemplateResponse(
        "ordenes/nuevo.html",
        {
            "request": request,
            "clientes": clientes,
            "vehiculos": vehiculos
        }
    )

@router.post("/ordenes/nuevo")
def crear_orden_form(
    request: Request,
    descripcion: str = Form(...),
    cliente_id: int = Form(...),
    vehiculo_id: int = Form(...),
    db: Session = Depends(get_db)
):
    orden = OrdenTrabajo(
        descripcion=descripcion,
        cliente_id=cliente_id,
        vehiculo_id=vehiculo_id,
        estado="abierta",
        total=0.0
    )

    db.add(orden)
    db.commit()
    db.refresh(orden)

    return RedirectResponse(
        url=f"/ordenes/{orden.id}?created=1",
        status_code=303
    )

@router.get("/ordenes/{orden_id}", response_class=HTMLResponse)
def vista_detalle_orden(
    request: Request,
    orden_id: int,
    db: Session = Depends(get_db)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        return RedirectResponse("/ordenes", status_code=303)

    clientes = db.query(Cliente).order_by(Cliente.nombre.asc()).all()
    vehiculos = db.query(Vehiculo).order_by(Vehiculo.placa.asc()).all()

    return templates.TemplateResponse(
        "ordenes/detalle.html",
        {
            "request": request,
            "orden": orden,
            "clientes": clientes,
            "vehiculos": vehiculos
        }
    )

@router.get("/servicios/categorias", response_class=HTMLResponse)
def vista_categorias_servicio(request: Request):
    return templates.TemplateResponse(
        "servicios/categorias.html",
        {"request": request}
    )

@router.get("/servicios/{servicio_id}/editar", response_class=HTMLResponse)
def vista_editar_servicio(request: Request, servicio_id: int):
    return templates.TemplateResponse(
        "servicios/editar.html",
        {
            "request": request,
            "servicio_id": servicio_id
        }
    )



# =====================================
# LOGOUT
# =====================================
@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response
