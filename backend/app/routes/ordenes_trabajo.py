# ======================================================
# IMPORTS
# ======================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orden_trabajo import OrdenTrabajo
from app.schemas.orden_trabajo import (
    OrdenTrabajoCreate,
    OrdenTrabajoResponse
)

from app.core.security import admin_o_mecanico

# ======================================================
# ROUTER
# ======================================================
# ⚠️ IMPORTANTE:
# - AQUÍ NO SE CREA FastAPI()
# - AQUÍ NO SE USA app.include_router()
# - SOLO SE DEFINE router

router = APIRouter(
    prefix="/ordenes",
    tags=["Órdenes de Trabajo"]
)

# ======================================================
# CREAR ORDEN
# ======================================================

@router.post("/", response_model=OrdenTrabajoResponse)
def crear_orden(
    data: OrdenTrabajoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)  # 🔒 Admin o mecánico
):
    orden = OrdenTrabajo(**data.dict())
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden

# ======================================================
# LISTAR ÓRDENES
# ======================================================

@router.get("/", response_model=list[OrdenTrabajoResponse])
def listar_ordenes(
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    return db.query(OrdenTrabajo).all()

# ======================================================
# OBTENER ORDEN POR ID
# ======================================================

@router.get("/{orden_id}", response_model=OrdenTrabajoResponse)
def obtener_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    return orden

# ======================================================
# CAMBIAR ESTADO DE ORDEN
# ======================================================

@router.put("/{orden_id}/estado")
def cambiar_estado(
    orden_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    estados_validos = ["abierta", "en_proceso", "cerrada", "cancelada"]

    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Use: {estados_validos}"
        )

    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    orden.estado = nuevo_estado
    db.commit()

    return {
        "mensaje": "Estado actualizado correctamente",
        "estado": orden.estado
    }

# ======================================================
# REABRIR ORDEN (CONTROLADO)
# ======================================================

@router.put("/{orden_id}/reabrir")
def reabrir_orden(
    orden_id: int,
    motivo: str,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    if orden.estado != "cerrada":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden reabrir órdenes cerradas"
        )

    orden.estado = "en_proceso"
    orden.descripcion += f"\n\n[REAPERTURA]: {motivo}"

    db.commit()

    return {
        "mensaje": "Orden reabierta correctamente",
        "nuevo_estado": orden.estado
    }
