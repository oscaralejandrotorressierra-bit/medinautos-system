# ======================================================
# IMPORTS
# ======================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, time

from backend.app.core.database import get_db
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.models.servicio import Servicio

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

ESTADOS_FINALES = ["cerrada", "cancelada"]

def _rango_datetime(fecha_inicio: date | None, fecha_fin: date | None):
    inicio = datetime.combine(fecha_inicio, time.min) if fecha_inicio else None
    fin = datetime.combine(fecha_fin, time.max) if fecha_fin else None
    return inicio, fin

# ======================================================
# REPORTE 1 — INGRESOS TOTALES
# ======================================================

@router.get("/ingresos-totales")
def ingresos_totales(db: Session = Depends(get_db)):
    total = db.query(
        func.sum(OrdenTrabajo.total)
    ).filter(
        OrdenTrabajo.estado.in_(ESTADOS_FINALES)
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
    inicio, fin = _rango_datetime(fecha_inicio, fecha_fin)
    total = db.query(
        func.sum(OrdenTrabajo.total)
    ).filter(
        OrdenTrabajo.estado.in_(ESTADOS_FINALES),
        OrdenTrabajo.fecha >= inicio,
        OrdenTrabajo.fecha <= fin
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
        OrdenTrabajo.estado.in_(ESTADOS_FINALES)
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
def ordenes_cerradas(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    db: Session = Depends(get_db)
):
    inicio, fin = _rango_datetime(fecha_inicio, fecha_fin)
    query = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado.in_(ESTADOS_FINALES))
    if inicio:
        query = query.filter(OrdenTrabajo.fecha >= inicio)
    if fin:
        query = query.filter(OrdenTrabajo.fecha <= fin)
    ordenes = query.order_by(OrdenTrabajo.fecha.desc()).all()

    return [
        {
            "id": orden.id,
            "fecha": orden.fecha,
            "estado": orden.estado,
            "total": orden.total,
            "cliente": {"nombre": orden.cliente.nombre} if orden.cliente else None,
            "vehiculo": {"placa": orden.vehiculo.placa} if orden.vehiculo else None
        }
        for orden in ordenes
    ]
