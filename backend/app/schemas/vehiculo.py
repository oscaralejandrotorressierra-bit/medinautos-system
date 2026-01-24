from pydantic import BaseModel
from typing import Optional


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: Optional[int] = None
    cilindraje: Optional[int] = None
    clase: Optional[str] = None
    km_actual: Optional[int] = None
    cliente_id: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        from_attributes = True
