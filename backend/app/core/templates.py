"""
Configuración centralizada de Jinja2Templates para MedinAutos.
"""

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    directory="backend/app/templates"
)
