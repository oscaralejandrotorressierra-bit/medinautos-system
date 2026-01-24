"""
Configuración centralizada de Jinja2Templates para MedinAutos.
"""

import os
import sys

from fastapi.templating import Jinja2Templates


def _base_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "backend", "app")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


templates = Jinja2Templates(
    directory=os.path.join(_base_app_dir(), "templates")
)
