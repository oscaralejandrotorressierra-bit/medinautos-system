from backend.app.core.database import SessionLocal
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.servicio import Servicio


BASE_CATEGORIAS = {
    "Mecanica general": [
        "Cambio de aceite y filtro",
        "Cambio de bujias",
        "Cambio de correas (alternador/tiempos)",
        "Cambio de bomba de agua",
        "Cambio de radiador",
        "Revision de fugas",
        "Ajuste general de motor",
    ],
    "Frenos": [
        "Cambio de pastillas",
        "Cambio de discos",
        "Cambio de bandas",
        "Rectificacion de discos",
        "Cambio de liquido de frenos",
    ],
    "Suspension y direccion": [
        "Cambio de amortiguadores",
        "Cambio de terminales",
        "Cambio de rotulas",
        "Cambio de bujes",
    ],
    "Alineacion y balanceo": [
        "Alineacion",
        "Balanceo",
        "Rotacion de llantas",
    ],
    "Electricidad": [
        "Diagnostico electrico",
        "Cambio de bateria",
        "Cambio de alternador",
        "Cambio de arranque",
        "Cambio de luces",
    ],
    "Refrigeracion": [
        "Cambio de refrigerante",
        "Cambio de termostato",
        "Limpieza de radiador",
    ],
    "Transmision": [
        "Cambio de aceite de caja",
        "Revision de embrague",
        "Cambio de kit de embrague",
    ],
    "Aire acondicionado": [
        "Recarga de gas",
        "Revision de fugas",
        "Cambio de compresor",
    ],
    "Diagnostico": [
        "Escaneo computadorizado",
        "Revision general pre-viaje",
    ],
    "Carroceria": [
        "Latoneria menor",
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

            for servicio_nombre in servicios:
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
                        precio=0.0,
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
