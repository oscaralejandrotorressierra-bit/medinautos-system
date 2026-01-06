"""
Rutas del dashboard principal del sistema MedinAutos.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo

router = APIRouter()
templates = Jinja2Templates(directory="backend/app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Muestra el panel principal del sistema.
    """
    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {"request": request}
    )


@router.get("/dashboard/data")
def dashboard_data(db: Session = Depends(get_db)):
    """
    Retorna los datos reales del dashboard.
    """
    return {
        "clientes": db.query(Cliente).count(),
        "vehiculos": db.query(Vehiculo).count(),
        "estado": "Operativo"
    }
