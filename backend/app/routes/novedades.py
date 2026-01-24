"""
Rutas del modulo Novedades (mantenimiento por km/tiempo).
"""

from datetime import date

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.core.templates import templates
from backend.app.core.database import get_db
from backend.app.core.novedades import calcular_estado_regla
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.recomendacion_regla import RecomendacionRegla
from backend.app.models.vehiculo_recomendacion import VehiculoRecomendacion


router = APIRouter(tags=["Novedades"])


def _coerce_int(valor):
    if valor is None:
        return None
    if isinstance(valor, int):
        return valor
    texto = str(valor).strip()
    if not texto:
        return None
    return int(texto)


def _asegurar_recomendacion(db, vehiculo, regla):
    existente = db.query(VehiculoRecomendacion).filter(
        VehiculoRecomendacion.vehiculo_id == vehiculo.id,
        VehiculoRecomendacion.regla_id == regla.id
    ).first()
    if existente:
        return existente

    rec = VehiculoRecomendacion(
        vehiculo_id=vehiculo.id,
        regla_id=regla.id,
        km_base=vehiculo.km_actual or 0,
        fecha_base=date.today()
    )
    db.add(rec)
    return rec


@router.get("/novedades", response_class=HTMLResponse)
def vista_novedades(request: Request, db: Session = Depends(get_db)):
    reglas = db.query(RecomendacionRegla).order_by(RecomendacionRegla.nombre.asc()).all()
    vehiculos = db.query(Vehiculo).order_by(Vehiculo.placa.asc()).all()

    recs = db.query(VehiculoRecomendacion).all()
    rec_map = {(rec.vehiculo_id, rec.regla_id): rec for rec in recs}

    alertas = []
    for vehiculo in vehiculos:
        for regla in reglas:
            if not regla.activo:
                continue
            rec = rec_map.get((vehiculo.id, regla.id))
            if not rec:
                rec = _asegurar_recomendacion(db, vehiculo, regla)
                rec_map[(vehiculo.id, regla.id)] = rec

            estado = calcular_estado_regla(vehiculo, regla, rec)
            alertas.append({
                "vehiculo_id": vehiculo.id,
                "placa": vehiculo.placa,
                "marca": vehiculo.marca,
                "linea": vehiculo.modelo,
                "km_actual": vehiculo.km_actual,
                "regla_id": regla.id,
                "regla_nombre": regla.nombre,
                "descripcion": regla.descripcion,
                "estado": estado["estado"],
                "progreso": estado["progreso"],
                "km_restante": estado["km_restante"],
                "dias_restante": estado["dias_restante"],
                "km_trans": estado["km_trans"],
                "dias_trans": estado["dias_trans"],
            })

    db.commit()

    agrupadas = {}
    for alerta in alertas:
        vid = alerta["vehiculo_id"]
        if vid not in agrupadas:
            agrupadas[vid] = {
                "vehiculo_id": vid,
                "placa": alerta["placa"],
                "marca": alerta["marca"],
                "linea": alerta["linea"],
                "km_actual": alerta["km_actual"],
                "alertas": []
            }
        agrupadas[vid]["alertas"].append(alerta)

    return templates.TemplateResponse(
        "novedades/overview.html",
        {
            "request": request,
            "reglas": reglas,
            "alertas": alertas,
            "alertas_vehiculos": list(agrupadas.values())
        }
    )


@router.post("/novedades/reglas")
def crear_regla(
    nombre: str = Form(...),
    descripcion: str | None = Form(None),
    intervalo_km: int | None = Form(None),
    intervalo_dias: int | None = Form(None),
    tolerancia_km: int | None = Form(200),
    tolerancia_dias: int | None = Form(3),
    db: Session = Depends(get_db)
):
    intervalo_km = _coerce_int(intervalo_km)
    intervalo_dias = _coerce_int(intervalo_dias)
    tolerancia_km = _coerce_int(tolerancia_km)
    tolerancia_dias = _coerce_int(tolerancia_dias)

    if not intervalo_km and not intervalo_dias:
        return RedirectResponse("/novedades?rule_error=1", status_code=303)

    regla = RecomendacionRegla(
        nombre=nombre.strip(),
        descripcion=descripcion.strip() if descripcion else None,
        intervalo_km=intervalo_km,
        intervalo_dias=intervalo_dias,
        tolerancia_km=tolerancia_km if tolerancia_km is not None else 200,
        tolerancia_dias=tolerancia_dias if tolerancia_dias is not None else 3,
        activo=True
    )
    db.add(regla)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse("/novedades?rule_duplicate=1", status_code=303)
    db.refresh(regla)

    vehiculos = db.query(Vehiculo).all()
    for vehiculo in vehiculos:
        _asegurar_recomendacion(db, vehiculo, regla)

    db.commit()

    return RedirectResponse("/novedades?rule_created=1", status_code=303)


@router.post("/novedades/reglas/{regla_id}/editar")
def editar_regla(
    regla_id: int,
    nombre: str = Form(...),
    descripcion: str | None = Form(None),
    intervalo_km: int | None = Form(None),
    intervalo_dias: int | None = Form(None),
    tolerancia_km: int | None = Form(None),
    tolerancia_dias: int | None = Form(None),
    db: Session = Depends(get_db)
):
    regla = db.query(RecomendacionRegla).filter(RecomendacionRegla.id == regla_id).first()
    if not regla:
        return RedirectResponse("/novedades?rule_not_found=1", status_code=303)

    intervalo_km = _coerce_int(intervalo_km)
    intervalo_dias = _coerce_int(intervalo_dias)
    tolerancia_km = _coerce_int(tolerancia_km)
    tolerancia_dias = _coerce_int(tolerancia_dias)

    if not intervalo_km and not intervalo_dias:
        return RedirectResponse("/novedades?rule_error=1", status_code=303)

    regla.nombre = nombre.strip()
    regla.descripcion = descripcion.strip() if descripcion else None
    regla.intervalo_km = intervalo_km
    regla.intervalo_dias = intervalo_dias
    if tolerancia_km is not None:
        regla.tolerancia_km = tolerancia_km
    if tolerancia_dias is not None:
        regla.tolerancia_dias = tolerancia_dias

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse("/novedades?rule_duplicate=1", status_code=303)

    return RedirectResponse("/novedades?rule_updated=1", status_code=303)


@router.post("/novedades/reglas/{regla_id}/toggle")
def toggle_regla(
    regla_id: int,
    db: Session = Depends(get_db)
):
    regla = db.query(RecomendacionRegla).filter(RecomendacionRegla.id == regla_id).first()
    if not regla:
        return RedirectResponse("/novedades?rule_not_found=1", status_code=303)

    regla.activo = not regla.activo
    db.commit()

    return RedirectResponse("/novedades?rule_toggled=1", status_code=303)


@router.post("/novedades/reglas/{regla_id}/eliminar")
def eliminar_regla(
    regla_id: int,
    db: Session = Depends(get_db)
):
    regla = db.query(RecomendacionRegla).filter(RecomendacionRegla.id == regla_id).first()
    if not regla:
        return RedirectResponse("/novedades?rule_not_found=1", status_code=303)

    db.query(VehiculoRecomendacion).filter(
        VehiculoRecomendacion.regla_id == regla_id
    ).delete(synchronize_session=False)
    db.delete(regla)
    db.commit()

    return RedirectResponse("/novedades?rule_deleted=1", status_code=303)


@router.post("/novedades/{vehiculo_id}/reglas/{regla_id}/reset")
def reset_regla(
    vehiculo_id: int,
    regla_id: int,
    db: Session = Depends(get_db)
):
    rec = db.query(VehiculoRecomendacion).filter(
        VehiculoRecomendacion.vehiculo_id == vehiculo_id,
        VehiculoRecomendacion.regla_id == regla_id
    ).first()
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if rec and vehiculo:
        rec.km_base = vehiculo.km_actual or 0
        rec.fecha_base = date.today()
        db.commit()

    return RedirectResponse("/novedades?rule_reset=1", status_code=303)
