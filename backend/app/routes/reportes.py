# ======================================================
# IMPORTS
# ======================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.core.database import SessionLocal

from app.models.orden_trabajo import OrdenTrabajo
from app.models.detalle_orden import DetalleOrden
from app.models.servicio import Servicio

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
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
# REPORTE 1 — INGRESOS TOTALES
# ======================================================

@router.get("/ingresos-totales")
def ingresos_totales(db: Session = Depends(get_db)):
    total = db.query(
        func.sum(OrdenTrabajo.total)
    ).filter(
        OrdenTrabajo.estado == "cerrada"
    ).scalar() or 0

    return {
        "ingresos_totales": total
    }

# ======================================================
# REPORTE 2 — INGRESOS POR FECHAS
# ======================================================

@router.get("/ingresos-por-fecha")
def ingresos_por_fecha(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    total = db.query(
        func.sum(OrdenTrabajo.total)
    ).filter(
        OrdenTrabajo.estado == "cerrada",
        OrdenTrabajo.fecha >= fecha_inicio,
        OrdenTrabajo.fecha <= fecha_fin
    ).scalar() or 0

    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "ingresos": total
    }

# ======================================================
# REPORTE 3 — SERVICIOS MÁS VENDIDOS
# ======================================================

@router.get("/servicios-mas-vendidos")
def servicios_mas_vendidos(db: Session = Depends(get_db)):
    resultados = db.query(
        Servicio.nombre,
        func.sum(DetalleOrden.cantidad).label("cantidad_vendida"),
        func.sum(DetalleOrden.subtotal).label("total_generado")
    ).join(
        DetalleOrden, Servicio.id == DetalleOrden.servicio_id
    ).join(
        OrdenTrabajo, OrdenTrabajo.id == DetalleOrden.orden_id
    ).filter(
        OrdenTrabajo.estado == "cerrada"
    ).group_by(
        Servicio.nombre
    ).order_by(
        func.sum(DetalleOrden.cantidad).desc()
    ).all()

    return [
        {
            "servicio": r.nombre,
            "cantidad_vendida": r.cantidad_vendida,
            "total_generado": r.total_generado
        }
        for r in resultados
    ]

# ======================================================
# REPORTE 4 — ÓRDENES CERRADAS
# ======================================================

@router.get("/ordenes-cerradas")
def ordenes_cerradas(db: Session = Depends(get_db)):
    ordenes = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.estado == "cerrada"
    ).all()

    return ordenes
