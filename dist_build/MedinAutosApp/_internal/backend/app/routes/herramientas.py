"""
Rutas del modulo Herramientas
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import solo_admin
from backend.app.models.herramienta import Herramienta
from backend.app.models.mecanico import Mecanico
from backend.app.models.prestamo_herramienta import PrestamoHerramienta
from backend.app.schemas.herramienta import (
    HerramientaCreateSchema,
    HerramientaUpdateSchema,
    HerramientaResponseSchema,
)
from backend.app.schemas.prestamo_herramienta import (
    PrestamoHerramientaCreateSchema,
    PrestamoHerramientaDevolucionSchema,
    PrestamoHerramientaResponseSchema,
)


router = APIRouter(
    prefix="/herramientas",
    tags=["Herramientas"],
    dependencies=[Depends(solo_admin)],
)


@router.get("/", response_model=list[HerramientaResponseSchema])
def listar_herramientas(db: Session = Depends(get_db)):
    return db.query(Herramienta).all()


@router.get("/prestamos", response_model=list[PrestamoHerramientaResponseSchema])
def listar_prestamos(activos: bool = False, db: Session = Depends(get_db)):
    query = db.query(PrestamoHerramienta)
    if activos:
        query = query.filter(PrestamoHerramienta.fecha_devolucion.is_(None))
    return query.order_by(PrestamoHerramienta.fecha_prestamo.desc()).all()


@router.post("/prestamos", response_model=PrestamoHerramientaResponseSchema)
def crear_prestamo(
    data: PrestamoHerramientaCreateSchema,
    db: Session = Depends(get_db),
):
    herramienta = db.query(Herramienta).filter(Herramienta.id == data.herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")

    if not herramienta.activo:
        raise HTTPException(status_code=400, detail="Herramienta inactiva")

    prestamo_activo = db.query(PrestamoHerramienta).filter(
        PrestamoHerramienta.herramienta_id == herramienta.id,
        PrestamoHerramienta.fecha_devolucion.is_(None),
    ).first()
    if prestamo_activo:
        raise HTTPException(status_code=400, detail="Herramienta ya prestada")

    mecanico = db.query(Mecanico).filter(Mecanico.id == data.mecanico_id).first()
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    prestamo = PrestamoHerramienta(
        herramienta_id=data.herramienta_id,
        mecanico_id=data.mecanico_id,
        observaciones=data.observaciones,
    )
    herramienta.estado = "prestada"

    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return prestamo


@router.put("/prestamos/{prestamo_id}/devolver", response_model=PrestamoHerramientaResponseSchema)
@router.post("/prestamos/{prestamo_id}/devolver", response_model=PrestamoHerramientaResponseSchema)
def devolver_herramienta(
    prestamo_id: int,
    data: PrestamoHerramientaDevolucionSchema | None = None,
    db: Session = Depends(get_db),
):
    prestamo = db.query(PrestamoHerramienta).filter(PrestamoHerramienta.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")

    if prestamo.fecha_devolucion:
        raise HTTPException(status_code=400, detail="La herramienta ya fue devuelta")

    prestamo.fecha_devolucion = datetime.utcnow()
    if data and data.observaciones:
        prestamo.observaciones = data.observaciones

    herramienta = db.query(Herramienta).filter(Herramienta.id == prestamo.herramienta_id).first()
    if herramienta:
        herramienta.estado = "disponible"

    db.commit()
    db.refresh(prestamo)
    return prestamo

@router.get("/{herramienta_id}", response_model=HerramientaResponseSchema)
def obtener_herramienta(herramienta_id: int, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")
    return herramienta


@router.post("/", response_model=HerramientaResponseSchema)
def crear_herramienta(data: HerramientaCreateSchema, db: Session = Depends(get_db)):
    existente = db.query(Herramienta).filter(Herramienta.codigo == data.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El codigo ya existe")

    herramienta = Herramienta(**data.dict())
    db.add(herramienta)
    db.commit()
    db.refresh(herramienta)
    return herramienta


@router.put("/{herramienta_id}", response_model=HerramientaResponseSchema)
def actualizar_herramienta(
    herramienta_id: int,
    data: HerramientaUpdateSchema,
    db: Session = Depends(get_db),
):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(herramienta, campo, valor)

    db.commit()
    db.refresh(herramienta)
    return herramienta


@router.patch("/{herramienta_id}/toggle")
def toggle_herramienta(herramienta_id: int, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")

    herramienta.activo = not herramienta.activo
    db.commit()
    return {"id": herramienta.id, "activo": herramienta.activo}


@router.delete("/{herramienta_id}")
def eliminar_herramienta(herramienta_id: int, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")

    db.delete(herramienta)
    db.commit()
    return {"mensaje": "Herramienta eliminada correctamente"}
