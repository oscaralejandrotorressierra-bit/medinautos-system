from pydantic import BaseModel
from typing import Optional


class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float


class ServicioCreate(ServicioBase):
    pass


class ServicioResponse(ServicioBase):
    id: int

    class Config:
        orm_mode = True
