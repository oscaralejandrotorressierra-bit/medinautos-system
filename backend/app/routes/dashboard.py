"""
Rutas del dashboard principal del sistema MedinAutos.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from backend.app.core.templates import templates
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.cliente import Cliente
from datetime import date, datetime, timedelta

from backend.app.models.vehiculo import Vehiculo
from backend.app.models.mecanico import Mecanico
from backend.app.models.recomendacion_regla import RecomendacionRegla
from backend.app.models.vehiculo_recomendacion import VehiculoRecomendacion
from backend.app.core.novedades import calcular_estado_regla
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.models.servicio import Servicio
from backend.app.models.movimiento_caja import MovimientoCaja
from sqlalchemy import func

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Muestra el panel principal del sistema.
    """
    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {"request": request}
    )


@router.get("/dashboard/data")
def dashboard_data(db: Session = Depends(get_db)):
    """
    Retorna los datos reales del dashboard.
    """
    hoy = date.today()
    ahora = datetime.now()

    tecnicos = db.query(Mecanico).filter(Mecanico.fecha_nacimiento.isnot(None)).all()
    cumple_hoy = []
    cumple_proximos = []

    for tecnico in tecnicos:
        fecha = tecnico.fecha_nacimiento
        if not fecha:
            continue
        cumple_este_anio = fecha.replace(year=hoy.year)
        if cumple_este_anio < hoy:
            cumple_este_anio = fecha.replace(year=hoy.year + 1)

        dias = (cumple_este_anio - hoy).days
        data = {
            "id": tecnico.id,
            "nombre": f"{tecnico.nombres} {tecnico.apellidos}".strip(),
            "telefono": tecnico.telefono,
            "fecha": cumple_este_anio.isoformat()
        }
        if dias == 0:
            cumple_hoy.append(data)
        elif 0 < dias <= 7:
            cumple_proximos.append(data)

    reglas = db.query(RecomendacionRegla).filter(RecomendacionRegla.activo == True).all()
    recs = db.query(VehiculoRecomendacion).all()
    rec_map = {(rec.vehiculo_id, rec.regla_id): rec for rec in recs}

    alertas_vencidas = []
    alertas_vencidas_map = {}
    alertas_proximas_total = 0
    vehiculos = db.query(Vehiculo).all()
    for vehiculo in vehiculos:
        for regla in reglas:
            rec = rec_map.get((vehiculo.id, regla.id))
            if not rec:
                continue
            estado = calcular_estado_regla(vehiculo, regla, rec)
            if estado["estado"] == "proximo":
                alertas_proximas_total += 1
            if estado["estado"] != "vencido":
                continue
            if vehiculo.id not in alertas_vencidas_map:
                alerta = {
                    "vehiculo_id": vehiculo.id,
                    "placa": vehiculo.placa,
                    "cliente": vehiculo.cliente.nombre if vehiculo.cliente else "-",
                    "telefono": vehiculo.cliente.telefono if vehiculo.cliente and vehiculo.cliente.telefono else "-",
                    "total": 1
                }
                alertas_vencidas_map[vehiculo.id] = alerta
                alertas_vencidas.append(alerta)
            else:
                alertas_vencidas_map[vehiculo.id]["total"] += 1

    ordenes_total = db.query(OrdenTrabajo).count()
    ordenes_abiertas = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado == "abierta").count()
    ordenes_proceso = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado == "en_proceso").count()
    ordenes_cerradas = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado == "cerrada").count()
    ordenes_canceladas = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado == "cancelada").count()

    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = db.query(func.coalesce(func.sum(MovimientoCaja.monto), 0)).filter(
        MovimientoCaja.tipo == "ingreso",
        MovimientoCaja.fecha >= inicio_mes
    ).scalar()
    egresos_mes = db.query(func.coalesce(func.sum(MovimientoCaja.monto), 0)).filter(
        MovimientoCaja.tipo == "egreso",
        MovimientoCaja.fecha >= inicio_mes
    ).scalar()
    utilidad_mes = (ingresos_mes or 0) - (egresos_mes or 0)

    inicio_semana = (ahora - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    ingresos_semana_raw = db.query(
        func.date(MovimientoCaja.fecha).label("dia"),
        func.coalesce(func.sum(MovimientoCaja.monto), 0).label("total")
    ).filter(
        MovimientoCaja.tipo == "ingreso",
        MovimientoCaja.fecha >= inicio_semana
    ).group_by(func.date(MovimientoCaja.fecha)).all()
    egresos_semana_raw = db.query(
        func.date(MovimientoCaja.fecha).label("dia"),
        func.coalesce(func.sum(MovimientoCaja.monto), 0).label("total")
    ).filter(
        MovimientoCaja.tipo == "egreso",
        MovimientoCaja.fecha >= inicio_semana
    ).group_by(func.date(MovimientoCaja.fecha)).all()

    ingresos_map = {str(row.dia): float(row.total or 0) for row in ingresos_semana_raw}
    egresos_map = {str(row.dia): float(row.total or 0) for row in egresos_semana_raw}
    ingresos_semana = []
    for offset in range(6, -1, -1):
        dia = hoy - timedelta(days=offset)
        key = dia.isoformat()
        ingresos_semana.append({
            "dia": key,
            "ingresos": ingresos_map.get(key, 0),
            "egresos": egresos_map.get(key, 0)
        })

    top_servicios_raw = db.query(
        Servicio.nombre.label("nombre"),
        func.sum(DetalleOrden.subtotal).label("total"),
        func.sum(DetalleOrden.cantidad).label("cantidad")
    ).join(DetalleOrden, DetalleOrden.servicio_id == Servicio.id).group_by(
        Servicio.id
    ).order_by(func.sum(DetalleOrden.subtotal).desc()).limit(5).all()
    top_servicios = [
        {
            "nombre": row.nombre,
            "total": float(row.total or 0),
            "cantidad": int(row.cantidad or 0)
        }
        for row in top_servicios_raw
    ]

    return {
        "clientes": db.query(Cliente).count(),
        "vehiculos": db.query(Vehiculo).count(),
        "ordenes_total": ordenes_total,
        "ordenes_abiertas": ordenes_abiertas,
        "ordenes_proceso": ordenes_proceso,
        "ordenes_cerradas": ordenes_cerradas,
        "ordenes_canceladas": ordenes_canceladas,
        "ingresos_mes": float(ingresos_mes or 0),
        "egresos_mes": float(egresos_mes or 0),
        "utilidad_mes": float(utilidad_mes or 0),
        "ingresos_semana": ingresos_semana,
        "top_servicios": top_servicios,
        "cumple_hoy": cumple_hoy,
        "cumple_proximos": cumple_proximos,
        "cumple_hoy_total": len(cumple_hoy),
        "cumple_proximos_total": len(cumple_proximos),
        "alertas_vencidas": alertas_vencidas,
        "alertas_vencidas_total": sum(item["total"] for item in alertas_vencidas),
        "alertas_proximas_total": alertas_proximas_total,
        "estado": "Operativo"
    }
