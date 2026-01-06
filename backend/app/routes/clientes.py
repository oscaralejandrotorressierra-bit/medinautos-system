"""
Rutas de Clientes - MedinAutos
CRUD completo con protección por sesión (JWT en cookie)
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, engine
from backend.app.models.cliente import Cliente
from backend.app.core.templates import templates

# 🔐 DEPENDENCIA DE SEGURIDAD
from backend.app.core.security import usuario_autenticado

# Crear tablas si no existen (solo se ejecuta una vez)
Cliente.metadata.create_all(bind=engine)

# ======================================================
# ROUTER
# Se protege TODO el CRUD con usuario_autenticado
# ======================================================
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(usuario_autenticado)]
)

# ===============================
# DEPENDENCIA DB
# ===============================
def get_db():
    """
    Crea y cierra la sesión de base de datos.
    Se usa como dependencia en las rutas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================
# LISTAR CLIENTES
# ===============================
@router.get("/", response_class=HTMLResponse)
def listar_clientes(request: Request, db: Session = Depends(get_db)):
    """
    Muestra el listado de clientes registrados.
    (Requiere usuario autenticado)
    """
    clientes = db.query(Cliente).all()

    return templates.TemplateResponse(
        "clientes/clientes.html",
        {
            "request": request,
            "clientes": clientes
        }
    )


# ===============================
# FORMULARIO NUEVO CLIENTE
# ===============================
@router.get("/nuevo", response_class=HTMLResponse)
def nuevo_cliente(request: Request):
    """
    Muestra el formulario para crear un nuevo cliente.
    """
    return templates.TemplateResponse(
        "clientes/cliente_form.html",
        {
            "request": request
        }
    )


# ===============================
# CREAR CLIENTE
# ===============================
@router.post("/nuevo")
def crear_cliente(
    request: Request,
    nombre: str = Form(...),
    documento: str = Form(...),
    telefono: str = Form(None),
    email: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Guarda un nuevo cliente en la base de datos.

    - Valida que el documento no esté duplicado.
    - Si hay error, retorna el formulario con SweetAlert.
    - Si se crea correctamente, redirige con ?success=1.
    """

    # 🔎 Validar documento duplicado
    cliente_existente = db.query(Cliente).filter(
        Cliente.documento == documento
    ).first()

    if cliente_existente:
        return templates.TemplateResponse(
            "clientes/cliente_form.html",
            {
                "request": request,
                "swal_error": "Ya existe un cliente registrado con este documento.",
                "nombre": nombre,
                "documento": documento,
                "telefono": telefono,
                "email": email,
            }
        )

    # ✅ Crear cliente
    cliente = Cliente(
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        email=email
    )

    db.add(cliente)
    db.commit()

    # 🔑 Redirección para SweetAlert de éxito
    return RedirectResponse(
        url="/clientes/?success=1",
        status_code=303
    )


# ===============================
# FORMULARIO EDITAR CLIENTE
# ===============================
@router.get("/{cliente_id}/editar", response_class=HTMLResponse)
def editar_cliente_form(
    request: Request,
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Muestra el formulario de edición del cliente,
    con los datos precargados.
    """

    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        return RedirectResponse("/clientes/", status_code=303)

    return templates.TemplateResponse(
        "clientes/cliente_form.html",
        {
            "request": request,
            "cliente": cliente,
            "modo_edicion": True
        }
    )


# ===============================
# ACTUALIZAR CLIENTE
# ===============================
@router.post("/{cliente_id}/editar")
def editar_cliente(
    request: Request,
    cliente_id: int,
    nombre: str = Form(...),
    documento: str = Form(...),
    telefono: str = Form(None),
    email: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Actualiza un cliente existente.

    - Valida documento duplicado (excepto el propio cliente).
    - Si hay error, muestra SweetAlert.
    - Si se actualiza correctamente, redirige con ?updated=1.
    """

    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        return RedirectResponse("/clientes/", status_code=303)

    # 🔎 Validar documento duplicado (excepto este cliente)
    documento_duplicado = db.query(Cliente).filter(
        Cliente.documento == documento,
        Cliente.id != cliente_id
    ).first()

    if documento_duplicado:
        return templates.TemplateResponse(
            "clientes/cliente_form.html",
            {
                "request": request,
                "cliente": cliente,
                "modo_edicion": True,
                "swal_error": "Ya existe otro cliente con este documento."
            }
        )

    # ✅ Actualizar datos
    cliente.nombre = nombre
    cliente.documento = documento
    cliente.telefono = telefono
    cliente.email = email

    db.commit()

    # 🔑 Redirección para SweetAlert de éxito
    return RedirectResponse(
        url="/clientes/?updated=1",
        status_code=303
    )


# ===============================
# ELIMINAR CLIENTE
# ===============================
@router.post("/{cliente_id}/eliminar")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina definitivamente un cliente.
    """

    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if cliente:
        db.delete(cliente)
        db.commit()

    # 🔑 Redirección para SweetAlert eliminado
    return RedirectResponse(
        url="/clientes/?deleted=1",
        status_code=303
    )
