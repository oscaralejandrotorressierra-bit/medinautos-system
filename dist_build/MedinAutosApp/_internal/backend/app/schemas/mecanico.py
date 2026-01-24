"""
Schema de validacion para Mecanicos
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class MecanicoBaseSchema(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    documento: str = Field(..., min_length=3, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    especialidad: Optional[str] = Field(None, max_length=80)
    fecha_ingreso: Optional[date] = None
    porcentaje_base: Optional[float] = Field(0.0, ge=0, le=100)


class MecanicoCreateSchema(MecanicoBaseSchema):
    pass


class MecanicoUpdateSchema(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    documento: Optional[str] = Field(None, min_length=3, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    especialidad: Optional[str] = Field(None, max_length=80)
    fecha_ingreso: Optional[date] = None
    porcentaje_base: Optional[float] = Field(None, ge=0, le=100)
    activo: Optional[bool] = None


class MecanicoResponseSchema(MecanicoBaseSchema):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class MecanicoResumenSchema(BaseModel):
    id: int
    nombres: str
    apellidos: str
    documento: str
    especialidad: Optional[str] = None
    activo: bool
    porcentaje_base: float

    class Config:
        from_attributes = True


class OrdenResumenSchema(BaseModel):
    id: int
    descripcion: str
    estado: str
    fecha: datetime

    class Config:
        from_attributes = True


class AsignacionMecanicoCreateSchema(BaseModel):
    observaciones: Optional[str] = Field(None, max_length=255)
    porcentaje: Optional[float] = Field(None, ge=0, le=100)


class AsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    porcentaje: float
    monto: float
    orden: OrdenResumenSchema
    mecanico: MecanicoResumenSchema

    class Config:
        from_attributes = True


class OrdenAsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    porcentaje: float
    monto: float
    orden: OrdenResumenSchema

    class Config:
        from_attributes = True


class MecanicoAsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    porcentaje: float
    monto: float
    mecanico: MecanicoResumenSchema

    class Config:
        from_attributes = True
