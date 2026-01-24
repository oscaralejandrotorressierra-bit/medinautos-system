"""
Rutas del modulo Mecanicos
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import admin_o_mecanico
from backend.app.models.mecanico import Mecanico
from backend.app.models.orden_mecanico import OrdenMecanico
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.schemas.mecanico import (
    MecanicoCreateSchema,
    MecanicoUpdateSchema,
    MecanicoResponseSchema,
    AsignacionMecanicoCreateSchema,
    AsignacionResponseSchema,
    OrdenAsignacionResponseSchema,
    MecanicoAsignacionResponseSchema,
)


router = APIRouter(
    prefix="/mecanicos",
    tags=["Mecanicos"],
    dependencies=[Depends(admin_o_mecanico)]
)


@router.get("/", response_model=list[MecanicoResponseSchema])
def listar_mecanicos(db: Session = Depends(get_db)):
    return db.query(Mecanico).all()


@router.get("/{mecanico_id}", response_model=MecanicoResponseSchema)
def obtener_mecanico(mecanico_id: int, db: Session = Depends(get_db)):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()

    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    return mecanico


@router.post("/", response_model=MecanicoResponseSchema)
def crear_mecanico(data: MecanicoCreateSchema, db: Session = Depends(get_db)):
    existente = db.query(Mecanico).filter(Mecanico.documento == data.documento).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un mecanico con ese documento")

    mecanico = Mecanico(**data.dict())
    db.add(mecanico)
    db.commit()
    db.refresh(mecanico)

    return mecanico


@router.put("/{mecanico_id}", response_model=MecanicoResponseSchema)
def actualizar_mecanico(
    mecanico_id: int,
    data: MecanicoUpdateSchema,
    db: Session = Depends(get_db)
):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()

    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(mecanico, campo, valor)

    db.commit()
    db.refresh(mecanico)
    return mecanico


@router.patch("/{mecanico_id}/toggle")
def toggle_mecanico(mecanico_id: int, db: Session = Depends(get_db)):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()

    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    mecanico.activo = not mecanico.activo
    db.commit()

    return {"id": mecanico.id, "activo": mecanico.activo}


@router.delete("/{mecanico_id}")
def eliminar_mecanico(mecanico_id: int, db: Session = Depends(get_db)):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()

    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    db.delete(mecanico)
    db.commit()

    return {"mensaje": "Mecanico eliminado correctamente"}


@router.post(
    "/{mecanico_id}/asignar/{orden_id}",
    response_model=AsignacionResponseSchema
)
def asignar_mecanico_a_orden(
    mecanico_id: int,
    orden_id: int,
    data: AsignacionMecanicoCreateSchema,
    db: Session = Depends(get_db)
):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    orden = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    existente = db.query(OrdenMecanico).filter(
        OrdenMecanico.orden_id == orden_id,
        OrdenMecanico.mecanico_id == mecanico_id
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="El mecanico ya esta asignado a la orden")

    porcentaje = data.porcentaje if data.porcentaje is not None else mecanico.porcentaje_base
    monto = (orden.total or 0.0) * (porcentaje / 100.0)

    asignacion = OrdenMecanico(
        orden_id=orden_id,
        mecanico_id=mecanico_id,
        porcentaje=porcentaje,
        monto=monto,
        observaciones=data.observaciones
    )

    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)

    return asignacion


@router.delete("/{mecanico_id}/asignar/{orden_id}")
def quitar_mecanico_de_orden(
    mecanico_id: int,
    orden_id: int,
    db: Session = Depends(get_db)
):
    asignacion = db.query(OrdenMecanico).filter(
        OrdenMecanico.orden_id == orden_id,
        OrdenMecanico.mecanico_id == mecanico_id
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")

    db.delete(asignacion)
    db.commit()

    return {"mensaje": "Mecanico desasignado correctamente"}


@router.get(
    "/{mecanico_id}/ordenes",
    response_model=list[OrdenAsignacionResponseSchema]
)
def listar_ordenes_por_mecanico(mecanico_id: int, db: Session = Depends(get_db)):
    mecanico = db.query(Mecanico).filter(Mecanico.id == mecanico_id).first()
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecanico no encontrado")

    return db.query(OrdenMecanico).filter(
        OrdenMecanico.mecanico_id == mecanico_id
    ).all()


@router.get(
    "/ordenes/{orden_id}",
    response_model=list[MecanicoAsignacionResponseSchema]
)
def listar_mecanicos_por_orden(orden_id: int, db: Session = Depends(get_db)):
    orden = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    return db.query(OrdenMecanico).filter(
        OrdenMecanico.orden_id == orden_id
    ).all()
