"""
Rutas del modulo contable
"""

import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from backend.app.core.templates import _base_app_dir
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import solo_admin
from backend.app.models.caja import Caja
from backend.app.models.liquidacion_mecanico import LiquidacionMecanico
from backend.app.models.liquidacion_mecanico_detalle import LiquidacionMecanicoDetalle
from backend.app.models.mecanico import Mecanico
from backend.app.models.movimiento_caja import MovimientoCaja
from backend.app.models.movimiento_proveedor import MovimientoProveedor
from backend.app.models.orden_mecanico import OrdenMecanico
from sqlalchemy import func

from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.schemas.caja import CajaCloseSchema, CajaCreateSchema, CajaResponseSchema
from backend.app.schemas.liquidacion_mecanico import (
    LiquidacionMecanicoCreateSchema,
    LiquidacionMecanicoResponseSchema,
)
from backend.app.schemas.movimiento_caja import (
    MovimientoCajaCreateSchema,
    MovimientoCajaResponseSchema,
)
from backend.app.schemas.movimiento_proveedor import (
    MovimientoProveedorCreateSchema,
    MovimientoProveedorResponseSchema,
)


router = APIRouter(
    prefix="/contabilidad",
    tags=["Contabilidad"],
    dependencies=[Depends(solo_admin)]
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

def _formatear_moneda(valor):
    return f"${(valor or 0):,.0f}".replace(",", ".")

def _obtener_carpeta_pdf_nomina():
    ruta = os.path.join("backend", "app", "static", "pdfs", "nomina")
    os.makedirs(ruta, exist_ok=True)
    return ruta

def _generar_pdf_nomina(liquidacion, mecanico, detalles, metodo_pago):
    ruta = os.path.join(_obtener_carpeta_pdf_nomina(), f"nomina_{liquidacion.id}.pdf")
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
        [Paragraph(f"<b>Liquidacion:</b> #{liquidacion.id}", styles["Normal"]),
         Paragraph(f"<b>Fecha:</b> {liquidacion.fecha_creacion.strftime('%Y-%m-%d %I:%M %p')}", styles["Normal"])]
    ], colWidths=[120, 380])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header)
    story.append(Spacer(1, 12))

    nombre_mecanico = "Tecnico"
    documento = "-"
    if mecanico:
        nombre_mecanico = f"{mecanico.nombres} {mecanico.apellidos}".strip()
        documento = mecanico.documento or "-"

    if metodo_pago == "efectivo":
        metodo_label = "Efectivo"
    elif metodo_pago == "transferencia":
        metodo_label = "Transferencia"
    elif metodo_pago:
        metodo_label = metodo_pago
    else:
        metodo_label = "No definido"

    info = Table([
        [Paragraph("<b>Recibo de pago de nomina</b>", styles["Normal"]), ""],
        [f"Tecnico: {nombre_mecanico}", f"Documento: {documento}"],
        [f"Periodo: {liquidacion.fecha_inicio} - {liquidacion.fecha_fin}", f"Frecuencia: {liquidacion.frecuencia}"],
        [f"Estado: {liquidacion.estado}", f"Metodo de pago: {metodo_label}"],
    ], colWidths=[260, 260])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(info)
    story.append(Spacer(1, 14))

    data = [["Orden", "%", "Base", "Monto"]]
    for det in detalles:
        data.append([
            f"#{det.orden_id}",
            f"{det.porcentaje}%",
            _formatear_moneda(det.base_calculo),
            _formatear_moneda(det.monto)
        ])
    if len(data) == 1:
        data.append(["-", "-", _formatear_moneda(0), _formatear_moneda(0)])

    tabla = Table(data, colWidths=[100, 80, 160, 160])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))
    story.append(Paragraph("<b>Detalle por orden</b>", styles["Heading4"]))
    story.append(tabla)
    story.append(Spacer(1, 12))

    resumen = Table([
        [Paragraph("<b>Total base</b>", styles["Normal"]), _formatear_moneda(liquidacion.total_base)],
        [Paragraph("<b>Total a pagar</b>", styles["Normal"]), _formatear_moneda(liquidacion.total_pagado)]
    ], colWidths=[400, 120])
    resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    story.append(resumen)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Firma tecnico: ____________________", styles["Normal"]))
    story.append(Paragraph("Firma y sello taller: ____________________", styles["Normal"]))

    doc.build(story)
    return ruta


@router.post("/cajas/abrir", response_model=CajaResponseSchema)
def abrir_caja(
    data: CajaCreateSchema,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    caja_abierta = db.query(Caja).filter(Caja.estado == "abierta").first()
    if caja_abierta:
        raise HTTPException(status_code=400, detail="Ya existe una caja abierta")

    caja = Caja(
        saldo_inicial=data.saldo_inicial,
        observaciones=data.observaciones,
        usuario_apertura=usuario.get("sub")
    )
    db.add(caja)
    db.commit()
    db.refresh(caja)
    return caja


@router.get("/cajas/abierta", response_model=CajaResponseSchema)
def obtener_caja_abierta(db: Session = Depends(get_db)):
    caja = db.query(Caja).filter(Caja.estado == "abierta").first()
    if not caja:
        raise HTTPException(status_code=404, detail="No hay caja abierta")
    return caja


@router.post("/cajas/{caja_id}/cerrar", response_model=CajaResponseSchema)
def cerrar_caja(
    caja_id: int,
    data: CajaCloseSchema,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    if caja.estado != "abierta":
        raise HTTPException(status_code=400, detail="La caja ya esta cerrada")

    ingresos = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.caja_id == caja.id,
        MovimientoCaja.tipo == "ingreso"
    ).scalar() or 0.0
    egresos = db.query(func.sum(MovimientoCaja.monto)).filter(
        MovimientoCaja.caja_id == caja.id,
        MovimientoCaja.tipo == "egreso"
    ).scalar() or 0.0

    saldo_calculado = caja.saldo_inicial + ingresos - egresos
    caja.saldo_final = data.saldo_final if data.saldo_final is not None else saldo_calculado
    caja.fecha_cierre = datetime.utcnow()
    caja.estado = "cerrada"
    caja.usuario_cierre = usuario.get("sub")
    if data.observaciones:
        caja.observaciones = data.observaciones

    db.commit()
    db.refresh(caja)
    return caja


@router.get("/cajas", response_model=list[CajaResponseSchema])
def listar_cajas(db: Session = Depends(get_db)):
    return db.query(Caja).order_by(Caja.id.desc()).all()


@router.post("/movimientos", response_model=MovimientoCajaResponseSchema)
def crear_movimiento_caja(
    data: MovimientoCajaCreateSchema,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    if data.caja_id:
        caja = db.query(Caja).filter(Caja.id == data.caja_id).first()
    else:
        caja = db.query(Caja).filter(Caja.estado == "abierta").first()

    if not caja:
        raise HTTPException(status_code=404, detail="No hay caja disponible")
    if caja.estado != "abierta":
        raise HTTPException(status_code=400, detail="La caja esta cerrada")

    if data.proveedor_id:
        cargos = db.query(func.sum(MovimientoProveedor.subtotal)).filter(
            MovimientoProveedor.proveedor_id == data.proveedor_id,
            MovimientoProveedor.tipo.in_(["cargo", "ajuste_cargo"])
        ).scalar() or 0.0
        pagos = db.query(func.sum(MovimientoProveedor.subtotal)).filter(
            MovimientoProveedor.proveedor_id == data.proveedor_id,
            MovimientoProveedor.tipo.in_(["pago", "abono", "ajuste_abono"])
        ).scalar() or 0.0
        saldo = cargos - pagos
        if data.monto > saldo:
            raise HTTPException(
                status_code=400,
                detail="El monto excede el saldo pendiente del proveedor"
            )

    movimiento = MovimientoCaja(
        caja_id=caja.id,
        tipo=data.tipo,
        concepto=data.concepto,
        monto=data.monto,
        motivo=data.motivo,
        orden_id=data.orden_id,
        proveedor_id=data.proveedor_id,
        usuario=usuario.get("sub")
    )
    db.add(movimiento)

    if data.proveedor_id:
        tipo_mov = "pago" if data.tipo == "egreso" else "abono"
        movimiento_proveedor = MovimientoProveedor(
            proveedor_id=data.proveedor_id,
            orden_id=data.orden_id,
            item_id=None,
            tipo=tipo_mov,
            cantidad=None,
            valor_unitario=None,
            subtotal=data.monto,
            motivo=data.motivo or data.concepto,
            usuario=usuario.get("sub")
        )
        db.add(movimiento_proveedor)

    db.flush()
    _actualizar_saldo_caja(db, caja)

    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.get("/movimientos", response_model=list[MovimientoCajaResponseSchema])
def listar_movimientos_caja(
    caja_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(MovimientoCaja)
    if caja_id is not None:
        query = query.filter(MovimientoCaja.caja_id == caja_id)
    return query.order_by(MovimientoCaja.fecha.desc()).all()


@router.post("/proveedores/movimientos", response_model=MovimientoProveedorResponseSchema)
def crear_movimiento_proveedor(
    data: MovimientoProveedorCreateSchema,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    tipos_validos = {"cargo", "pago", "abono", "ajuste_cargo", "ajuste_abono"}
    if data.tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo invalido. Use: {sorted(tipos_validos)}")

    movimiento = MovimientoProveedor(
        proveedor_id=data.proveedor_id,
        orden_id=data.orden_id,
        item_id=data.item_id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        valor_unitario=data.valor_unitario,
        subtotal=data.subtotal,
        motivo=data.motivo,
        usuario=usuario.get("sub")
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.get("/proveedores/{proveedor_id}/movimientos", response_model=list[MovimientoProveedorResponseSchema])
def listar_movimientos_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    return db.query(MovimientoProveedor).filter(
        MovimientoProveedor.proveedor_id == proveedor_id
    ).order_by(MovimientoProveedor.fecha.desc()).all()


@router.get("/proveedores/{proveedor_id}/saldo")
def saldo_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    cargos = db.query(func.sum(MovimientoProveedor.subtotal)).filter(
        MovimientoProveedor.proveedor_id == proveedor_id,
        MovimientoProveedor.tipo.in_(["cargo", "ajuste_cargo"])
    ).scalar() or 0.0
    pagos = db.query(func.sum(MovimientoProveedor.subtotal)).filter(
        MovimientoProveedor.proveedor_id == proveedor_id,
        MovimientoProveedor.tipo.in_(["pago", "abono", "ajuste_abono"])
    ).scalar() or 0.0
    saldo = cargos - pagos
    return {
        "proveedor_id": proveedor_id,
        "saldo": saldo,
        "cargos": cargos,
        "pagos": pagos
    }


@router.post("/liquidaciones/mecanicos", response_model=LiquidacionMecanicoResponseSchema)
def crear_liquidacion_mecanico(
    data: LiquidacionMecanicoCreateSchema,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    mecanico = db.query(Mecanico).filter(Mecanico.id == data.mecanico_id).first()
    if not mecanico:
        raise HTTPException(status_code=404, detail="Tecnico no encontrado")

    asignaciones = db.query(OrdenMecanico, OrdenTrabajo).join(
        OrdenTrabajo, OrdenTrabajo.id == OrdenMecanico.orden_id
    ).filter(
        OrdenMecanico.mecanico_id == data.mecanico_id,
        OrdenTrabajo.estado == "cerrada",
        OrdenTrabajo.fecha >= data.fecha_inicio,
        OrdenTrabajo.fecha <= data.fecha_fin
    ).all()

    liquidacion = LiquidacionMecanico(
        mecanico_id=data.mecanico_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        frecuencia=data.frecuencia,
        usuario=usuario.get("sub"),
        observaciones=data.observaciones
    )
    db.add(liquidacion)
    db.flush()

    total_base = 0.0
    total_pagado = 0.0

    for asignacion, orden in asignaciones:
        porcentaje = asignacion.porcentaje if asignacion.porcentaje > 0 else mecanico.porcentaje_base
        base = db.query(func.sum(DetalleOrden.subtotal)).filter(
            DetalleOrden.orden_id == orden.id
        ).scalar() or 0.0
        monto = base * (porcentaje / 100.0)

        detalle = LiquidacionMecanicoDetalle(
            liquidacion_id=liquidacion.id,
            orden_id=orden.id,
            porcentaje=porcentaje,
            base_calculo=base,
            monto=monto
        )
        db.add(detalle)
        total_base += base
        total_pagado += monto

    liquidacion.total_base = total_base
    liquidacion.total_pagado = total_pagado

    db.commit()
    db.refresh(liquidacion)
    return liquidacion


@router.get("/liquidaciones/mecanicos", response_model=list[LiquidacionMecanicoResponseSchema])
def listar_liquidaciones_mecanicos(
    mecanico_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(LiquidacionMecanico)
    if mecanico_id is not None:
        query = query.filter(LiquidacionMecanico.mecanico_id == mecanico_id)
    return query.order_by(LiquidacionMecanico.fecha_creacion.desc()).all()


@router.get("/liquidaciones/mecanicos/{liquidacion_id}", response_model=LiquidacionMecanicoResponseSchema)
def obtener_liquidacion_mecanico(liquidacion_id: int, db: Session = Depends(get_db)):
    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.id == liquidacion_id
    ).first()
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidacion no encontrada")
    return liquidacion

@router.get("/liquidaciones/mecanicos/{liquidacion_id}/pdf")
def descargar_pdf_liquidacion(
    liquidacion_id: int,
    metodo_pago: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.id == liquidacion_id
    ).first()
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidacion no encontrada")

    mecanico = db.query(Mecanico).filter(
        Mecanico.id == liquidacion.mecanico_id
    ).first()

    detalles = db.query(LiquidacionMecanicoDetalle).filter(
        LiquidacionMecanicoDetalle.liquidacion_id == liquidacion.id
    ).order_by(LiquidacionMecanicoDetalle.id.asc()).all()

    ruta = _generar_pdf_nomina(
        liquidacion=liquidacion,
        mecanico=mecanico,
        detalles=detalles,
        metodo_pago=metodo_pago
    )

    return FileResponse(
        path=ruta,
        filename=f"nomina_{liquidacion.id}.pdf",
        media_type="application/pdf"
    )


@router.patch("/liquidaciones/mecanicos/{liquidacion_id}/estado")
def actualizar_estado_liquidacion(
    liquidacion_id: int,
    estado: str,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    estados_validos = ["pendiente", "pagado"]
    if estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado invalido. Use: {estados_validos}"
        )

    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.id == liquidacion_id
    ).first()
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidacion no encontrada")

    if estado == "pagado":
        if liquidacion.estado == "pagado":
            raise HTTPException(
                status_code=400,
                detail="La liquidacion ya esta marcada como pagada"
            )
        caja = db.query(Caja).filter(Caja.estado == "abierta").first()
        if not caja:
            raise HTTPException(
                status_code=400,
                detail="Debe existir una caja abierta para pagar la nomina"
            )

        mecanico = db.query(Mecanico).filter(
            Mecanico.id == liquidacion.mecanico_id
        ).first()
        nombre_mecanico = "Tecnico"
        if mecanico:
            nombre_mecanico = f"{mecanico.nombres} {mecanico.apellidos}".strip()

        movimiento = MovimientoCaja(
            caja_id=caja.id,
            tipo="egreso",
            concepto=f"Pago nomina tecnico {nombre_mecanico}",
            monto=liquidacion.total_pagado or 0.0,
            motivo="Pago de liquidacion",
            orden_id=None,
            proveedor_id=None,
            usuario=usuario.get("sub")
        )
        db.add(movimiento)
        db.flush()
        _actualizar_saldo_caja(db, caja)

    liquidacion.estado = estado
    db.commit()

    return {"id": liquidacion.id, "estado": liquidacion.estado}
