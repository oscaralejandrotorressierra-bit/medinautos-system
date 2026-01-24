"""
Utilidades para calcular alertas de mantenimiento.
"""

from datetime import date


def calcular_estado_regla(vehiculo, regla, rec, hoy=None):
    hoy = hoy or date.today()
    km_intervalo = regla.intervalo_km or 0
    dias_intervalo = regla.intervalo_dias or 0
    tolerancia_km = regla.tolerancia_km or 0
    tolerancia_dias = regla.tolerancia_dias or 0

    km_base = rec.km_base if rec and rec.km_base is not None else (vehiculo.km_actual or 0)
    fecha_base = rec.fecha_base if rec and rec.fecha_base else hoy

    km_actual = vehiculo.km_actual if vehiculo.km_actual is not None else None
    dias_trans = (hoy - fecha_base).days if fecha_base else 0
    km_trans = 0
    if km_actual is not None:
        km_trans = max(km_actual - km_base, 0)

    km_progress = (km_trans / km_intervalo) if km_intervalo else 0
    dias_progress = (dias_trans / dias_intervalo) if dias_intervalo else 0
    progreso = min(max(km_progress, dias_progress, 0), 1)

    km_vencido = km_intervalo and km_trans >= km_intervalo
    dias_vencido = dias_intervalo and dias_trans >= dias_intervalo

    km_proximo = km_intervalo and km_trans >= max(km_intervalo - tolerancia_km, 0)
    dias_proximo = dias_intervalo and dias_trans >= max(dias_intervalo - tolerancia_dias, 0)

    if km_vencido or dias_vencido:
        estado = "vencido"
    elif km_proximo or dias_proximo:
        estado = "proximo"
    else:
        estado = "ok"

    km_restante = km_intervalo - km_trans if km_intervalo else None
    dias_restante = dias_intervalo - dias_trans if dias_intervalo else None

    return {
        "estado": estado,
        "progreso": int(progreso * 100),
        "km_restante": km_restante,
        "dias_restante": dias_restante,
        "km_trans": km_trans,
        "dias_trans": dias_trans,
    }


def construir_alerta_vehiculo(vehiculo, regla, rec):
    estado = calcular_estado_regla(vehiculo, regla, rec)
    return {
        "vehiculo_id": vehiculo.id,
        "placa": vehiculo.placa,
        "marca": vehiculo.marca,
        "linea": vehiculo.modelo,
        "regla_id": regla.id,
        "regla_nombre": regla.nombre,
        "descripcion": regla.descripcion,
        "estado": estado["estado"],
        "progreso": estado["progreso"],
        "km_restante": estado["km_restante"],
        "dias_restante": estado["dias_restante"],
        "km_trans": estado["km_trans"],
        "dias_trans": estado["dias_trans"],
    }
