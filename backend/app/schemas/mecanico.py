"""
Schema de validacion para Mecanicos
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class MecanicoBaseSchema(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    documento: str = Field(..., min_length=3, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    especialidad: Optional[str] = Field(None, max_length=80)
    fecha_ingreso: Optional[date] = None


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


class AsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    orden: OrdenResumenSchema
    mecanico: MecanicoResumenSchema

    class Config:
        from_attributes = True


class OrdenAsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    orden: OrdenResumenSchema

    class Config:
        from_attributes = True


class MecanicoAsignacionResponseSchema(BaseModel):
    id: int
    fecha_asignacion: datetime
    observaciones: Optional[str] = None
    mecanico: MecanicoResumenSchema

    class Config:
        from_attributes = True
