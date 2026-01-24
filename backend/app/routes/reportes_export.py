# ======================================================
# IMPORTS
# ======================================================

import os
from datetime import datetime, date, time

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from backend.app.core.templates import _base_app_dir
from sqlalchemy.orm import Session
from openpyxl import Workbook

from backend.app.core.database import get_db
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.core.security import solo_admin

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes Exportables"]
)

ESTADOS_FINALES = ["cerrada", "cancelada"]


def _rango_datetime(fecha_inicio: date | None, fecha_fin: date | None):
    inicio = datetime.combine(fecha_inicio, time.min) if fecha_inicio else None
    fin = datetime.combine(fecha_fin, time.max) if fecha_fin else None
    return inicio, fin


def _formatear_moneda(valor):
    return f"${(valor or 0):,.0f}".replace(",", ".")


def _formatear_fecha(valor):
    if not valor:
        return "-"
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %I:%M %p")
    return str(valor)

# ======================================================
# REPORTE PDF - ORDENES FINALIZADAS
# ======================================================

@router.get("/ordenes-cerradas/pdf")
def reporte_ordenes_pdf(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    carpeta = os.path.join("backend", "app", "static", "pdfs", "reportes")
    os.makedirs(carpeta, exist_ok=True)
    archivo = os.path.join(carpeta, "ordenes_cerradas.pdf")

    doc = SimpleDocTemplate(archivo, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    logo_path = os.path.join(_base_app_dir(), "static", "img", "logo_medinautos.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=60)
    else:
        logo = Paragraph("MEDINAUTOS", styles["Heading2"])

    header = Table([
        [logo, Paragraph("<b>MEDINAUTOS</b><br/>Telefono: 3166191371", styles["Normal"])],
        [Paragraph("<b>Reporte de ordenes finalizadas</b>", styles["Heading3"]), ""],
    ], colWidths=[120, 420])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    rango = "Todos los registros"
    if fecha_inicio and fecha_fin:
        rango = f"{fecha_inicio} a {fecha_fin}"
    elif fecha_inicio:
        rango = f"Desde {fecha_inicio}"
    elif fecha_fin:
        rango = f"Hasta {fecha_fin}"

    info = Table([
        ["Rango:", rango],
        ["Generado:", datetime.utcnow().strftime("%Y-%m-%d %I:%M %p")]
    ], colWidths=[90, 450])
    info.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
    ]))
    story.append(info)
    story.append(Spacer(1, 12))

    inicio, fin = _rango_datetime(fecha_inicio, fecha_fin)
    query = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado.in_(ESTADOS_FINALES))
    if inicio:
        query = query.filter(OrdenTrabajo.fecha >= inicio)
    if fin:
        query = query.filter(OrdenTrabajo.fecha <= fin)
    ordenes = query.order_by(OrdenTrabajo.fecha.desc()).all()

    data = [["Orden", "Fecha", "Estado", "Cliente", "Vehiculo", "Total"]]
    total_acumulado = 0.0
    for orden in ordenes:
        cliente = orden.cliente.nombre if orden.cliente else "-"
        vehiculo = orden.vehiculo.placa if orden.vehiculo else "-"
        total = orden.total or 0.0
        total_acumulado += total
        data.append([
            f"#{orden.id}",
            _formatear_fecha(orden.fecha),
            (orden.estado or "-").capitalize(),
            cliente,
            vehiculo,
            _formatear_moneda(total)
        ])

    if len(data) == 1:
        data.append(["-", "-", "-", "-", "-", _formatear_moneda(0)])

    tabla = Table(data, colWidths=[60, 130, 80, 160, 85, 90])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (5, 1), (5, -1), "RIGHT"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 12))

    resumen = Table([
        ["Total ordenes:", str(len(ordenes))],
        ["Total generado:", _formatear_moneda(total_acumulado)]
    ], colWidths=[140, 150])
    resumen.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(resumen)

    doc.build(story)

    return FileResponse(
        path=archivo,
        filename=os.path.basename(archivo),
        media_type="application/pdf"
    )

# ======================================================
# REPORTE EXCEL - INGRESOS
# ======================================================

@router.get("/ingresos/excel")
def reporte_ingresos_excel(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    carpeta = os.path.join("backend", "app", "static", "pdfs", "reportes")
    os.makedirs(carpeta, exist_ok=True)
    archivo = os.path.join(carpeta, "ingresos_medinautos.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Ingresos"

    # Encabezados
    ws.append(["ID Orden", "Fecha", "Estado", "Total"])

    inicio, fin = _rango_datetime(fecha_inicio, fecha_fin)
    query = db.query(OrdenTrabajo).filter(OrdenTrabajo.estado.in_(ESTADOS_FINALES))
    if inicio:
        query = query.filter(OrdenTrabajo.fecha >= inicio)
    if fin:
        query = query.filter(OrdenTrabajo.fecha <= fin)
    ordenes = query.all()

    for orden in ordenes:
        ws.append([
            orden.id,
            _formatear_fecha(orden.fecha),
            orden.estado,
            orden.total
        ])

    wb.save(archivo)

    return FileResponse(
        path=archivo,
        filename=os.path.basename(archivo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
