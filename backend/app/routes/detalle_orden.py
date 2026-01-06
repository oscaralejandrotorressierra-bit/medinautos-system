# ======================================================
# IMPORTS
# ======================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import SessionLocal

from app.models.detalle_orden import DetalleOrden
from app.models.orden_trabajo import OrdenTrabajo
from app.models.servicio import Servicio

from app.schemas.detalle_orden import (
    DetalleOrdenCreate,
    DetalleOrdenResponse
)

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/detalle-orden",
    tags=["Detalle de Orden"]
)

# ======================================================
# DEPENDENCIA BD
# ======================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# AGREGAR SERVICIO A ORDEN (CON BLOQUEO)
# ======================================================

@router.post("/", response_model=DetalleOrdenResponse)
def agregar_servicio_a_orden(
    detalle: DetalleOrdenCreate,
    db: Session = Depends(get_db)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == detalle.orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no existe")

    # 🔒 BLOQUEO SI ESTÁ CERRADA
    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una orden cerrada. Reabra la orden primero."
        )

    servicio = db.query(Servicio).filter(
        Servicio.id == detalle.servicio_id
    ).first()

    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no existe")

    subtotal = servicio.precio * detalle.cantidad

    nuevo_detalle = DetalleOrden(
        orden_id=detalle.orden_id,
        servicio_id=detalle.servicio_id,
        cantidad=detalle.cantidad,
        precio_unitario=servicio.precio,
        subtotal=subtotal
    )

    db.add(nuevo_detalle)

    orden.total += subtotal

    db.commit()
    db.refresh(nuevo_detalle)

    return nuevo_detalle

# ======================================================
# LISTAR SERVICIOS DE UNA ORDEN
# ======================================================

@router.get("/orden/{orden_id}", response_model=List[DetalleOrdenResponse])
def listar_detalle_por_orden(
    orden_id: int,
    db: Session = Depends(get_db)
):
    return db.query(DetalleOrden).filter(
        DetalleOrden.orden_id == orden_id
    ).all()

# ======================================================
# EDITAR SERVICIO DE ORDEN (CON BLOQUEO)
# ======================================================

@router.put("/{detalle_id}", response_model=DetalleOrdenResponse)
def editar_detalle_orden(
    detalle_id: int,
    cantidad: int,
    db: Session = Depends(get_db)
):
    detalle = db.query(DetalleOrden).filter(
        DetalleOrden.id == detalle_id
    ).first()

    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == detalle.orden_id
    ).first()

    # 🔒 BLOQUEO SI ESTÁ CERRADA
    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede editar una orden cerrada. Reabra la orden primero."
        )

    orden.total -= detalle.subtotal

    detalle.cantidad = cantidad
    detalle.subtotal = detalle.precio_unitario * cantidad

    orden.total += detalle.subtotal

    db.commit()
    db.refresh(detalle)

    return detalle

# ======================================================
# ELIMINAR SERVICIO DE ORDEN (CON BLOQUEO)
# ======================================================

@router.delete("/{detalle_id}")
def eliminar_detalle_orden(
    detalle_id: int,
    db: Session = Depends(get_db)
):
    detalle = db.query(DetalleOrden).filter(
        DetalleOrden.id == detalle_id
    ).first()

    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == detalle.orden_id
    ).first()

    # 🔒 BLOQUEO SI ESTÁ CERRADA
    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar servicios de una orden cerrada. Reabra la orden primero."
        )

    orden.total -= detalle.subtotal

    db.delete(detalle)
    db.commit()

    return {"mensaje": "Servicio eliminado de la orden correctamente"}
