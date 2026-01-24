from backend.app.core.database import SessionLocal
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.servicio import Servicio


BASE_CATEGORIAS = {
    "Mecanica general": [
        ("Cambio de aceite y filtro", 90000),
        ("Cambio de bujias", 70000),
        ("Cambio de correas", 120000),
        ("Cambio de bomba de agua", 180000),
        ("Cambio de radiador", 220000),
        ("Revision de fugas", 60000),
        ("Ajuste general de motor", 250000),
        ("Cambio de filtro de aire", 40000),
        ("Cambio de filtro de cabina", 35000),
        ("Cambio de filtro de combustible", 80000),
    ],
    "Frenos": [
        ("Cambio de pastillas", 120000),
        ("Cambio de discos", 180000),
        ("Cambio de bandas", 100000),
        ("Rectificacion de discos", 90000),
        ("Cambio de liquido de frenos", 60000),
        ("Revision de frenos", 50000),
    ],
    "Suspension y direccion": [
        ("Cambio de amortiguadores", 200000),
        ("Cambio de terminales", 120000),
        ("Cambio de rotulas", 120000),
        ("Cambio de bujes", 100000),
        ("Revision de suspension", 60000),
        ("Revision de direccion", 60000),
    ],
    "Alineacion y balanceo": [
        ("Alineacion", 60000),
        ("Balanceo", 50000),
        ("Rotacion de llantas", 40000),
    ],
    "Llantas": [
        ("Montaje de llantas", 50000),
        ("Reparacion de llantas", 30000),
        ("Calibracion de presion", 15000),
        ("Revision de desgaste", 20000),
    ],
    "Electricidad": [
        ("Diagnostico electrico", 80000),
        ("Cambio de bateria", 70000),
        ("Cambio de alternador", 220000),
        ("Cambio de arranque", 220000),
        ("Cambio de luces", 30000),
        ("Revision de cableado", 90000),
    ],
    "Refrigeracion": [
        ("Cambio de refrigerante", 70000),
        ("Cambio de termostato", 90000),
        ("Limpieza de radiador", 120000),
        ("Revision de mangueras", 50000),
    ],
    "Transmision": [
        ("Cambio de aceite de caja", 120000),
        ("Revision de embrague", 90000),
        ("Cambio de kit de embrague", 450000),
        ("Revision de transmision", 120000),
    ],
    "Aire acondicionado": [
        ("Recarga de gas", 120000),
        ("Revision de fugas", 90000),
        ("Cambio de compresor", 600000),
        ("Cambio de filtro de cabina", 35000),
    ],
    "Inyeccion y combustible": [
        ("Limpieza de inyectores", 150000),
        ("Revision de bomba de combustible", 100000),
        ("Limpieza de cuerpo de aceleracion", 90000),
    ],
    "Escape": [
        ("Revision de escape", 60000),
        ("Cambio de silenciador", 180000),
        ("Reparacion de fugas", 70000),
    ],
    "Diagnostico": [
        ("Escaneo computadorizado", 60000),
        ("Revision general pre-viaje", 80000),
        ("Diagnostico de motor", 100000),
    ],
    "Carroceria": [
        ("Latoneria menor", 120000),
        ("Ajuste de puertas", 70000),
        ("Reparacion de golpes", 180000),
    ],
    "Pintura": [
        ("Pulido general", 150000),
        ("Pintura por panel", 250000),
        ("Retoque de pintura", 90000),
    ],
    "Vidrios y cerraduras": [
        ("Cambio de parabrisas", 350000),
        ("Cambio de vidrio lateral", 250000),
        ("Reparacion de cerradura", 90000),
    ],
}


def seed_servicios_base():
    db = SessionLocal()
    try:
        for categoria_nombre, servicios in BASE_CATEGORIAS.items():
            categoria = (
                db.query(CategoriaServicio)
                .filter(CategoriaServicio.nombre == categoria_nombre)
                .first()
            )
            if not categoria:
                categoria = CategoriaServicio(
                    nombre=categoria_nombre,
                    descripcion=f"Categoria {categoria_nombre}",
                    activo=True,
                )
                db.add(categoria)
                db.flush()

            for servicio_nombre, precio in servicios:
                existente = (
                    db.query(Servicio)
                    .filter(Servicio.nombre == servicio_nombre)
                    .first()
                )
                if existente:
                    continue
                db.add(
                    Servicio(
                        nombre=servicio_nombre,
                        descripcion=f"Servicio {servicio_nombre}",
                        precio=float(precio),
                        categoria=categoria_nombre,
                        activo=True,
                    )
                )

        db.commit()
        print("Servicios y categorias base cargados.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_servicios_base()
