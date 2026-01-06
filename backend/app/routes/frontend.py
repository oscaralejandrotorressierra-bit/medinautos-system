"""
Rutas Frontend - Autenticación
Sistema MedinAutos
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from backend.app.core.database import get_db
from backend.app.models.usuario import Usuario
from backend.app.core.security import (
    verificar_password,
    crear_token,
    usuario_autenticado
)

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="backend/app/templates")


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


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


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response
