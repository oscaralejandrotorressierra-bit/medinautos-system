from datetime import date, timedelta

from backend.app.core.database import SessionLocal
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.cliente import Cliente
from backend.app.models.recomendacion_regla import RecomendacionRegla
from backend.app.models.vehiculo_recomendacion import VehiculoRecomendacion


def seed_novedades_demo():
    db = SessionLocal()
    try:
        reglas = db.query(RecomendacionRegla).filter(RecomendacionRegla.activo == True).all()
        if not reglas:
            print("No hay reglas activas para novedades.")
            return

        cliente = db.query(Cliente).first()
        if not cliente:
            print("No hay clientes para asociar vehiculos demo.")
            return

        vehiculos_existentes = db.query(Vehiculo).all()
        vehiculos_demo = []
        if len(vehiculos_existentes) >= 2:
            vehiculos_demo = vehiculos_existentes[:2]
        else:
            for idx in range(2):
                placa = f"DEMO{idx + 1}23"
                existente = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
                if existente:
                    vehiculos_demo.append(existente)
                    continue
                vehiculo = Vehiculo(
                    placa=placa,
                    marca="Demo",
                    modelo=f"Linea {idx + 1}",
                    anio=2022,
                    color="Gris",
                    cilindraje=1600,
                    clase="Particular",
                    km_actual=5000 + (idx * 8000),
                    cliente_id=cliente.id
                )
                db.add(vehiculo)
                db.flush()
                vehiculos_demo.append(vehiculo)

        hoy = date.today()
        for i, vehiculo in enumerate(vehiculos_demo):
            for regla in reglas:
                rec = db.query(VehiculoRecomendacion).filter(
                    VehiculoRecomendacion.vehiculo_id == vehiculo.id,
                    VehiculoRecomendacion.regla_id == regla.id
                ).first()
                if rec:
                    continue
                km_base = max((vehiculo.km_actual or 0) - (regla.intervalo_km or 0) + (500 * i), 0)
                fecha_base = hoy - timedelta(days=max((regla.intervalo_dias or 0) - (2 * i), 0))
                db.add(VehiculoRecomendacion(
                    vehiculo_id=vehiculo.id,
                    regla_id=regla.id,
                    km_base=km_base,
                    fecha_base=fecha_base
                ))

        db.commit()
        print("Datos demo de novedades cargados.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_novedades_demo()
