"""
Schemas Cliente
"""

from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nombre: str
    documento: str
    telefono: str | None = None
    email: str | None = None
