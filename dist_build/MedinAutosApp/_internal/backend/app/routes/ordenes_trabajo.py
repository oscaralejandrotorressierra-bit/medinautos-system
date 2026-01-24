# ======================================================
# IMPORTS
# ======================================================

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.caja import Caja
from backend.app.models.detalle_almacen import DetalleAlmacen
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.orden_mecanico import OrdenMecanico
from backend.app.models.mecanico import Mecanico
from backend.app.models.movimiento_caja import MovimientoCaja
from backend.app.models.proveedor import Proveedor
from backend.app.models.liquidacion_mecanico import LiquidacionMecanico
from backend.app.models.liquidacion_mecanico_detalle import LiquidacionMecanicoDetalle
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.servicio import Servicio
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from backend.app.schemas.orden_trabajo import (
    OrdenTrabajoCreate,
    OrdenTrabajoUpdate,
    OrdenTrabajoResponse
)
from backend.app.models.detalle_orden import DetalleOrden

from backend.app.core.security import admin_o_mecanico
from backend.app.core.templates import _base_app_dir

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

def _actualizar_saldo_caja(db: Session, caja: Caja):
    ingresos = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.caja_id == caja.id,
        MovimientoCaja.tipo == "ingreso"
    ).scalar() or 0.0
    egresos = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.caja_id == caja.id,
        MovimientoCaja.tipo == "egreso"
    ).scalar() or 0.0
    caja.saldo_final = caja.saldo_inicial + ingresos - egresos

def _calcular_periodo(fecha):
    import calendar
    inicio = fecha.replace(day=1)
    if fecha.day <= 15:
        fin = fecha.replace(day=15)
        frecuencia = "quincenal"
    else:
        ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
        fin = fecha.replace(day=ultimo_dia)
        frecuencia = "quincenal"
    return inicio, fin, frecuencia

def _obtener_o_crear_liquidacion(db: Session, mecanico_id: int, fecha_base):
    fecha_inicio, fecha_fin, frecuencia = _calcular_periodo(fecha_base)
    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.mecanico_id == mecanico_id,
        LiquidacionMecanico.fecha_inicio == fecha_inicio,
        LiquidacionMecanico.fecha_fin == fecha_fin,
        LiquidacionMecanico.estado == "pendiente"
    ).first()
    if liquidacion:
        return liquidacion

    liquidacion = LiquidacionMecanico(
        mecanico_id=mecanico_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        frecuencia=frecuencia,
        total_base=0.0,
        total_pagado=0.0,
        estado="pendiente"
    )
    db.add(liquidacion)
    db.flush()
    return liquidacion

def _recalcular_liquidacion(db: Session, liquidacion_id: int):
    totales = db.query(
        func.sum(LiquidacionMecanicoDetalle.base_calculo).label("base"),
        func.sum(LiquidacionMecanicoDetalle.monto).label("monto")
    ).filter(
        LiquidacionMecanicoDetalle.liquidacion_id == liquidacion_id
    ).first()
    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.id == liquidacion_id
    ).first()
    if not liquidacion:
        return
    liquidacion.total_base = totales.base or 0.0
    liquidacion.total_pagado = totales.monto or 0.0

def _formatear_moneda(valor):
    return f"${(valor or 0):,.0f}".replace(",", ".")

def _obtener_carpeta_pdf():
    ruta = os.path.join("backend", "app", "static", "pdfs", "ordenes")
    os.makedirs(ruta, exist_ok=True)
    return ruta

def _generar_pdf_orden(orden, cliente, vehiculo, servicios, insumos):
    ruta = os.path.join(_obtener_carpeta_pdf(), f"orden_{orden.id}.pdf")
    doc = SimpleDocTemplate(ruta, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    logo_path = os.path.join(_base_app_dir(), "static", "img", "logo_medinautos.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=60)
    else:
        logo = Paragraph("MEDINAUTOS", styles["Heading2"])

    header = Table([
        [logo, Paragraph("<b>MEDINAUTOS</b><br/>Telefono: 3166191371", styles["Normal"])],
        [Paragraph(f"<b>Orden:</b> #{orden.id}", styles["Normal"]),
         Paragraph(f"<b>Fecha:</b> {orden.fecha.strftime('%Y-%m-%d') if orden.fecha else '-'}", styles["Normal"])]
    ], colWidths=[120, 380])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header)
    story.append(Spacer(1, 12))

    if orden.forma_pago == "efectivo":
        forma_pago = "Efectivo"
    elif orden.forma_pago == "transferencia":
        forma_pago = "Transferencia"
    else:
        forma_pago = orden.forma_pago or "No definida"
    info = Table([
        [Paragraph("<b>Cliente</b>", styles["Normal"]), ""],
        [f"{cliente.nombre if cliente else '-'}", f"Documento: {cliente.documento if cliente else '-'}"],
        [f"Telefono: {cliente.telefono if cliente and cliente.telefono else '-'}", f"Email: {cliente.email if cliente and cliente.email else '-'}"],
        ["", ""],
        [Paragraph("<b>Vehiculo</b>", styles["Normal"]), ""],
        [f"Placa: {vehiculo.placa if vehiculo else '-'}", f"Marca: {vehiculo.marca if vehiculo else '-'}"],
        [f"Modelo: {vehiculo.modelo if vehiculo else '-'}", f"Ano: {vehiculo.anio if vehiculo and vehiculo.anio else '-'}"],
        ["", ""],
        [Paragraph("<b>Forma de pago</b>", styles["Normal"]), forma_pago],
    ], colWidths=[260, 260])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 4), (-1, 4), colors.whitesmoke),
        ("BACKGROUND", (0, 8), (-1, 8), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(info)
    story.append(Spacer(1, 14))

    def tabla_detalle(titulo, filas):
        story.append(Paragraph(f"<b>{titulo}</b>", styles["Heading4"]))
        data = [["Descripcion", "Cantidad", "Precio", "Subtotal"]]
        for fila in filas:
            data.append(fila)
        tabla = Table(data, colWidths=[260, 80, 90, 90])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 10))

    if servicios:
        filas = [[
            s["nombre"],
            s["cantidad"],
            _formatear_moneda(s["precio"]),
            _formatear_moneda(s["subtotal"])
        ] for s in servicios]
        tabla_detalle("Servicios", filas)

    if insumos:
        filas = [[
            i["nombre"],
            i["cantidad"],
            _formatear_moneda(i["precio"]),
            _formatear_moneda(i["subtotal"])
        ] for i in insumos]
        tabla_detalle("Insumos", filas)

    total = orden.total or 0.0
    resumen = Table([[Paragraph("<b>Total</b>", styles["Normal"]), _formatear_moneda(total)]], colWidths=[400, 120])
    resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(Spacer(1, 8))
    story.append(resumen)
    if orden.descripcion:
        descripcion = orden.descripcion.replace("\n", "<br/>")
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Observaciones</b>", styles["Heading4"]))
        story.append(Paragraph(descripcion, styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Firma cliente: ____________________", styles["Normal"]))
    story.append(Paragraph("Firma y sello taller: ____________________", styles["Normal"]))

    doc.build(story)
    return ruta

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
# PDF ORDEN
# ======================================================

@router.get("/{orden_id}/pdf")
def descargar_pdf_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    detalles_servicios = db.query(DetalleOrden).filter(
        DetalleOrden.orden_id == orden.id
    ).all()
    servicios = []
    for detalle in detalles_servicios:
        nombre = detalle.servicio.nombre if detalle.servicio else "Servicio"
        servicios.append({
            "nombre": nombre,
            "cantidad": detalle.cantidad,
            "precio": detalle.precio_unitario,
            "subtotal": detalle.subtotal
        })

    detalles_insumos = db.query(DetalleAlmacen).filter(
        DetalleAlmacen.orden_id == orden.id
    ).all()
    insumos = []
    for detalle in detalles_insumos:
        nombre = detalle.item.nombre if detalle.item else "Insumo"
        insumos.append({
            "nombre": nombre,
            "cantidad": detalle.cantidad,
            "precio": detalle.precio_unitario,
            "subtotal": detalle.subtotal
        })

    ruta = _generar_pdf_orden(
        orden=orden,
        cliente=orden.cliente,
        vehiculo=orden.vehiculo,
        servicios=servicios,
        insumos=insumos
    )

    return FileResponse(
        path=ruta,
        filename=f"orden_{orden.id}.pdf",
        media_type="application/pdf"
    )

# ======================================================
# ACTUALIZAR ORDEN
# ======================================================

@router.put("/{orden_id}", response_model=OrdenTrabajoResponse)
def actualizar_orden(
    orden_id: int,
    data: OrdenTrabajoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(orden, campo, valor)

    db.commit()
    db.refresh(orden)
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

    if nuevo_estado == "cancelada" and orden.estado != "cancelada":
        caja = db.query(Caja).filter(Caja.estado == "abierta").first()
        if not caja:
            raise HTTPException(
                status_code=400,
                detail="Debe existir una caja abierta para cancelar la orden"
            )

        ingreso = MovimientoCaja(
            caja_id=caja.id,
            tipo="ingreso",
            concepto=f"Ingreso por orden {orden.id}",
            monto=orden.total or 0.0,
            motivo=f"Cambio de estado a {nuevo_estado}",
            orden_id=orden.id,
            usuario=usuario.get("sub")
        )
        db.add(ingreso)

        total_proveedor = db.query(func.sum(DetalleAlmacen.subtotal_proveedor)).filter(
            DetalleAlmacen.orden_id == orden.id
        ).scalar() or 0.0

        proveedores_nombres = db.query(Proveedor.nombre).join(
            DetalleAlmacen, DetalleAlmacen.proveedor_id == Proveedor.id
        ).filter(
            DetalleAlmacen.orden_id == orden.id,
            Proveedor.id.isnot(None)
        ).distinct().all()
        proveedores_texto = ", ".join(sorted({p[0] for p in proveedores_nombres})) or "Proveedor"

        if total_proveedor > 0:
            egreso_proveedores = MovimientoCaja(
                caja_id=caja.id,
                tipo="egreso",
                concepto=f"Pago pendiente proveedor {proveedores_texto} orden {orden.id}",
                monto=total_proveedor,
                motivo=f"Cambio de estado a {nuevo_estado}",
                orden_id=orden.id,
                usuario=usuario.get("sub")
            )
            db.add(egreso_proveedores)

        asignaciones = db.query(OrdenMecanico, Mecanico).join(
            Mecanico, Mecanico.id == OrdenMecanico.mecanico_id
        ).filter(OrdenMecanico.orden_id == orden.id).all()

        total_mecanicos = 0.0
        nombres_mecanicos = []
        liquidaciones_actualizadas = set()
        for asignacion, mecanico in asignaciones:
            porcentaje = asignacion.porcentaje or mecanico.porcentaje_base or 0.0
            monto = (orden.total or 0.0) * (porcentaje / 100.0)
            asignacion.porcentaje = porcentaje
            asignacion.monto = monto
            total_mecanicos += monto
            nombres_mecanicos.append(f"{mecanico.nombres} {mecanico.apellidos}".strip())

            if monto > 0:
                fecha_base = (orden.fecha or datetime.utcnow()).date()
                liquidacion = _obtener_o_crear_liquidacion(
                    db, mecanico_id=asignacion.mecanico_id, fecha_base=fecha_base
                )
                detalle = db.query(LiquidacionMecanicoDetalle).filter(
                    LiquidacionMecanicoDetalle.liquidacion_id == liquidacion.id,
                    LiquidacionMecanicoDetalle.orden_id == orden.id
                ).first()
                if detalle:
                    detalle.porcentaje = porcentaje
                    detalle.base_calculo = orden.total or 0.0
                    detalle.monto = monto
                else:
                    db.add(LiquidacionMecanicoDetalle(
                        liquidacion_id=liquidacion.id,
                        orden_id=orden.id,
                        porcentaje=porcentaje,
                        base_calculo=orden.total or 0.0,
                        monto=monto
                    ))
                liquidaciones_actualizadas.add(liquidacion.id)

        if liquidaciones_actualizadas:
            db.flush()
            for liquidacion_id in liquidaciones_actualizadas:
                _recalcular_liquidacion(db, liquidacion_id)

        if total_mecanicos > 0:
            nombres_unicos = ", ".join(sorted(set(nombres_mecanicos))) or "Mecanico"
            egreso_mecanicos = MovimientoCaja(
                caja_id=caja.id,
                tipo="egreso",
                concepto=f"Pago pendiente mecanico {nombres_unicos} orden {orden.id}",
                monto=total_mecanicos,
                motivo=f"Cambio de estado a {nuevo_estado}",
                orden_id=orden.id,
                usuario=usuario.get("sub")
            )
            db.add(egreso_mecanicos)

        db.flush()
        _actualizar_saldo_caja(db, caja)

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

    caja = db.query(Caja).filter(Caja.estado == "abierta").first()
    if not caja:
        raise HTTPException(
            status_code=400,
            detail="Debe existir una caja abierta para reabrir la orden"
        )

    ingreso_total = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.orden_id == orden.id,
        MovimientoCaja.tipo == "ingreso",
        MovimientoCaja.concepto == f"Ingreso por orden {orden.id}"
    ).scalar() or 0.0

    proveedores_total = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.orden_id == orden.id,
        MovimientoCaja.tipo == "egreso",
        MovimientoCaja.concepto == f"Provision proveedores orden {orden.id}"
    ).scalar() or 0.0

    mecanicos_total = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.orden_id == orden.id,
        MovimientoCaja.tipo == "egreso",
        MovimientoCaja.concepto == f"Provision mecanicos orden {orden.id}"
    ).scalar() or 0.0

    if ingreso_total > 0:
        reverso_existente = db.query(MovimientoCaja).filter(
            MovimientoCaja.orden_id == orden.id,
            MovimientoCaja.tipo == "egreso",
            MovimientoCaja.concepto == f"Reversion ingreso orden {orden.id}"
        ).first()
        if not reverso_existente:
            db.add(MovimientoCaja(
                caja_id=caja.id,
                tipo="egreso",
                concepto=f"Reversion ingreso orden {orden.id}",
                monto=ingreso_total,
                motivo=motivo,
                orden_id=orden.id,
                usuario=usuario.get("sub")
            ))

    if proveedores_total > 0:
        reverso_existente = db.query(MovimientoCaja).filter(
            MovimientoCaja.orden_id == orden.id,
            MovimientoCaja.tipo == "ingreso",
            MovimientoCaja.concepto == f"Reversion provision proveedores orden {orden.id}"
        ).first()
        if not reverso_existente:
            db.add(MovimientoCaja(
                caja_id=caja.id,
                tipo="ingreso",
                concepto=f"Reversion provision proveedores orden {orden.id}",
                monto=proveedores_total,
                motivo=motivo,
                orden_id=orden.id,
                usuario=usuario.get("sub")
            ))

    if mecanicos_total > 0:
        reverso_existente = db.query(MovimientoCaja).filter(
            MovimientoCaja.orden_id == orden.id,
            MovimientoCaja.tipo == "ingreso",
            MovimientoCaja.concepto == f"Reversion provision mecanicos orden {orden.id}"
        ).first()
        if not reverso_existente:
            db.add(MovimientoCaja(
                caja_id=caja.id,
                tipo="ingreso",
                concepto=f"Reversion provision mecanicos orden {orden.id}",
                monto=mecanicos_total,
                motivo=motivo,
                orden_id=orden.id,
                usuario=usuario.get("sub")
            ))

    db.query(OrdenMecanico).filter(
        OrdenMecanico.orden_id == orden.id
    ).update({OrdenMecanico.monto: 0.0})

    pendientes = db.query(LiquidacionMecanicoDetalle.liquidacion_id).join(
        LiquidacionMecanico,
        LiquidacionMecanico.id == LiquidacionMecanicoDetalle.liquidacion_id
    ).filter(
        LiquidacionMecanicoDetalle.orden_id == orden.id,
        LiquidacionMecanico.estado == "pendiente"
    ).all()
    if pendientes:
        db.query(LiquidacionMecanicoDetalle).filter(
            LiquidacionMecanicoDetalle.orden_id == orden.id,
            LiquidacionMecanicoDetalle.liquidacion_id.in_([p[0] for p in pendientes])
        ).delete(synchronize_session=False)
        for liquidacion_id, in pendientes:
            _recalcular_liquidacion(db, liquidacion_id)

    db.flush()
    _actualizar_saldo_caja(db, caja)

    orden.estado = "en_proceso"
    orden.fecha_reapertura = datetime.utcnow()
    orden.descripcion += f"\n\n[REAPERTURA]: {motivo}"

    db.commit()

    return {
        "mensaje": "Orden reabierta correctamente",
        "nuevo_estado": orden.estado
    }

# ======================================================
# ELIMINAR ORDEN
# ======================================================

@router.delete("/{orden_id}")
def eliminar_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    db.query(DetalleOrden).filter(
        DetalleOrden.orden_id == orden_id
    ).delete(synchronize_session=False)

    db.delete(orden)
    db.commit()

    return {"mensaje": "Orden eliminada correctamente"}
