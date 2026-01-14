# ======================================================
# IMPORTS
# ======================================================

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook

from backend. app.core.database import get_db
from backend. app.models.orden_trabajo import OrdenTrabajo
from backend. app.core.security import solo_admin

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes Exportables"]
)

# ======================================================
# REPORTE PDF — ÓRDENES CERRADAS
# ======================================================

@router.get("/ordenes-cerradas/pdf")
def reporte_ordenes_pdf(
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    archivo = "ordenes_cerradas.pdf"
    c = canvas.Canvas(archivo, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "REPORTE DE ÓRDENES CERRADAS - MEDINAUTOS")

    c.setFont("Helvetica", 10)
    y = 720

    ordenes = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.estado == "cerrada"
    ).all()

    for orden in ordenes:
        texto = (
            f"Orden #{orden.id} | "
            f"Fecha: {orden.fecha} | "
            f"Total: ${orden.total:,.0f}"
        )
        c.drawString(50, y, texto)
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750

    c.save()

    return FileResponse(
        path=archivo,
        filename=archivo,
        media_type="application/pdf"
    )

# ======================================================
# REPORTE EXCEL — INGRESOS
# ======================================================

@router.get("/ingresos/excel")
def reporte_ingresos_excel(
    db: Session = Depends(get_db),
    usuario=Depends(solo_admin)
):
    archivo = "ingresos_medinautos.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Ingresos"

    # Encabezados
    ws.append(["ID Orden", "Fecha", "Total"])

    ordenes = db.query(OrdenTrabajo).filter(
        OrdenTrabajo.estado == "cerrada"
    ).all()

    for orden in ordenes:
        ws.append([
            orden.id,
            str(orden.fecha),
            orden.total
        ])

    wb.save(archivo)

    return FileResponse(
        path=archivo,
        filename=archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
