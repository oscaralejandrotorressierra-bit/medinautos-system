from pydantic import BaseModel
from typing import Optional


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: Optional[int] = None
    tipo: Optional[str] = None
    cliente_id: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        orm_mode = True
