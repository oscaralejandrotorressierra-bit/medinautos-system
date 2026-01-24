import random
from datetime import datetime, timedelta, date

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.security import encriptar_password
from backend.app.models.usuario import Usuario
from backend.app.models.cliente import Cliente
from backend.app.models.vehiculo import Vehiculo
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.models.servicio import Servicio
from backend.app.models.proveedor import Proveedor
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.mecanico import Mecanico
from backend.app.models.caja import Caja
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.models.detalle_orden import DetalleOrden
from backend.app.models.detalle_almacen import DetalleAlmacen
from backend.app.models.movimiento_caja import MovimientoCaja
from backend.app.models.movimiento_proveedor import MovimientoProveedor
from backend.app.models.orden_mecanico import OrdenMecanico
from backend.app.models.liquidacion_mecanico import LiquidacionMecanico
from backend.app.models.liquidacion_mecanico_detalle import LiquidacionMecanicoDetalle


def calcular_periodo(fecha):
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


def obtener_o_crear_liquidacion(db, mecanico_id, fecha_base):
    fecha_inicio, fecha_fin, frecuencia = calcular_periodo(fecha_base)
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


def recalcular_liquidacion(db, liquidacion_id):
    totales = db.query(
        LiquidacionMecanicoDetalle.base_calculo,
        LiquidacionMecanicoDetalle.monto
    ).filter(LiquidacionMecanicoDetalle.liquidacion_id == liquidacion_id).all()
    total_base = sum([t[0] or 0 for t in totales])
    total_pagado = sum([t[1] or 0 for t in totales])
    liquidacion = db.query(LiquidacionMecanico).filter(
        LiquidacionMecanico.id == liquidacion_id
    ).first()
    if liquidacion:
        liquidacion.total_base = total_base
        liquidacion.total_pagado = total_pagado


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin = Usuario(
            username="admin",
            password=encriptar_password("admin123"),
            rol="admin"
        )
        db.add(admin)

        categorias = [
            CategoriaServicio(nombre="Mecanica"),
            CategoriaServicio(nombre="Electricidad"),
            CategoriaServicio(nombre="Frenos"),
            CategoriaServicio(nombre="Suspension"),
            CategoriaServicio(nombre="Revision")
        ]
        db.add_all(categorias)
        db.flush()

        servicios_data = [
            ("Cambio de aceite", 85000),
            ("Alineacion", 60000),
            ("Balanceo", 45000),
            ("Revision general", 120000),
            ("Cambio pastillas", 180000),
            ("Cambio bateria", 250000),
            ("Diagnostico electrico", 90000),
            ("Cambio bujias", 110000),
            ("Cambio correa", 160000),
            ("Lavado motor", 70000),
            ("Cambio filtro aire", 50000),
            ("Revision frenos", 95000)
        ]
        servicios = []
        for idx, (nombre, precio) in enumerate(servicios_data):
            servicios.append(Servicio(
                nombre=nombre,
                descripcion=f"Servicio {nombre}",
                precio=precio,
                categoria=categorias[idx % len(categorias)].nombre,
                activo=True
            ))
        db.add_all(servicios)

        proveedores = [
            Proveedor(nombre="Repuestos Express", telefono="3105551111"),
            Proveedor(nombre="Motores Central", telefono="3105552222"),
            Proveedor(nombre="Autopartes Medellin", telefono="3105553333"),
            Proveedor(nombre="Frenos & Mas", telefono="3105554444"),
            Proveedor(nombre="Lubricantes Premium", telefono="3105555555")
        ]
        db.add_all(proveedores)
        db.flush()

        items_data = [
            ("Aceite motor", 15000, 22000, "Lubricantes"),
            ("Filtro aceite", 8000, 14000, "Filtros"),
            ("Filtro aire", 12000, 18000, "Filtros"),
            ("Pastillas freno", 45000, 65000, "Frenos"),
            ("Disco freno", 70000, 98000, "Frenos"),
            ("Bujias", 10000, 16000, "Encendido"),
            ("Correa alternador", 22000, 32000, "Motor"),
            ("Bateria", 160000, 210000, "Electricidad"),
            ("Amortiguador", 85000, 120000, "Suspension"),
            ("Liquido frenos", 12000, 20000, "Frenos"),
            ("Sensor oxigeno", 90000, 130000, "Electronica"),
            ("Radiador", 180000, 240000, "Refrigeracion"),
        ]
        items = []
        for idx, (nombre, valor_proveedor, valor_taller, categoria) in enumerate(items_data):
            proveedor = proveedores[idx % len(proveedores)]
            items.append(AlmacenItem(
                nombre=nombre,
                descripcion=f"{nombre} para taller",
                categoria=categoria,
                unidad="unidad",
                stock_actual=50,
                stock_minimo=5,
                valor_proveedor=valor_proveedor,
                valor_taller=valor_taller,
                proveedor_id=proveedor.id,
                activo=True
            ))
        db.add_all(items)

        clientes = []
        for i in range(1, 9):
            clientes.append(Cliente(
                nombre=f"Cliente {i}",
                documento=f"CC{i:04d}",
                telefono=f"300555{i:04d}",
                email=f"cliente{i}@correo.com"
            ))
        db.add_all(clientes)
        db.flush()

        vehiculos = []
        marcas = ["Mazda", "Chevrolet", "Renault", "Kia", "Toyota", "Hyundai"]
        for idx, cliente in enumerate(clientes):
            vehiculos.append(Vehiculo(
                placa=f"ABC{idx+1:03d}",
                marca=marcas[idx % len(marcas)],
                modelo=f"Modelo {idx+1}",
                color="Blanco",
                anio=2018 + (idx % 5),
                cliente_id=cliente.id
            ))
        db.add_all(vehiculos)

        mecanicos = []
        mecanicos_data = [
            ("Luis", "Ramirez", 25),
            ("Camilo", "Diaz", 30),
            ("Mateo", "Rojas", 28),
            ("Oscar", "Lopez", 22),
            ("Juan", "Perez", 26),
        ]
        for idx, (nombre, apellido, porcentaje) in enumerate(mecanicos_data):
            mecanicos.append(Mecanico(
                nombres=nombre,
                apellidos=apellido,
                documento=f"MEC{idx+1:03d}",
                telefono=f"311444{idx:03d}",
                especialidad="General",
                porcentaje_base=porcentaje
            ))
        db.add_all(mecanicos)
        db.flush()

        caja = Caja(
            saldo_inicial=1000000.0,
            observaciones="Caja de prueba",
            usuario_apertura="admin"
        )
        db.add(caja)
        db.flush()

        estados = ["cancelada"] * 6 + ["cerrada"] * 3 + ["en_proceso", "abierta", "cancelada"]
        random.shuffle(estados)

        for idx in range(12):
            fecha = datetime.utcnow() - timedelta(days=random.randint(0, 10))
            orden = OrdenTrabajo(
                descripcion=f"Orden de prueba #{idx+1}",
                cliente_id=clientes[idx % len(clientes)].id,
                vehiculo_id=vehiculos[idx % len(vehiculos)].id,
                estado=estados[idx],
                fecha=fecha,
                forma_pago=random.choice(["efectivo", "transferencia"])
            )
            db.add(orden)
            db.flush()

            servicios_sel = random.sample(servicios, 2)
            total = 0.0
            total_servicios = 0.0
            for srv in servicios_sel:
                cantidad = random.randint(1, 2)
                subtotal = srv.precio * cantidad
                total += subtotal
                total_servicios += subtotal
                db.add(DetalleOrden(
                    orden_id=orden.id,
                    servicio_id=srv.id,
                    cantidad=cantidad,
                    precio_unitario=srv.precio,
                    subtotal=subtotal
                ))

            insumos_sel = random.sample(items, 2)
            total_proveedor = 0.0
            proveedores_set = set()
            for ins in insumos_sel:
                cantidad = random.randint(1, 3)
                subtotal = ins.valor_taller * cantidad
                subtotal_proveedor = ins.valor_proveedor * cantidad
                total += subtotal
                total_proveedor += subtotal_proveedor
                if ins.proveedor and ins.proveedor.nombre:
                    proveedores_set.add(ins.proveedor.nombre)
                db.add(DetalleAlmacen(
                    orden_id=orden.id,
                    item_id=ins.id,
                    proveedor_id=ins.proveedor_id,
                    cantidad=cantidad,
                    precio_unitario=ins.valor_taller,
                    subtotal=subtotal,
                    costo_proveedor_unitario=ins.valor_proveedor,
                    subtotal_proveedor=subtotal_proveedor,
                    margen_subtotal=subtotal - subtotal_proveedor
                ))
                db.add(MovimientoProveedor(
                    proveedor_id=ins.proveedor_id,
                    orden_id=orden.id,
                    item_id=ins.id,
                    tipo="cargo",
                    cantidad=cantidad,
                    valor_unitario=ins.valor_proveedor,
                    subtotal=subtotal_proveedor,
                    motivo="Consumo en orden",
                    usuario="admin"
                ))

            orden.total = total

            asignados = random.sample(mecanicos, random.randint(1, 2))
            total_mecanicos = 0.0
            nombres_mecanicos = []
            liquidaciones = set()
            for mec in asignados:
                porcentaje = mec.porcentaje_base or 0
                monto = total_servicios * (porcentaje / 100.0)
                total_mecanicos += monto
                nombres_mecanicos.append(f"{mec.nombres} {mec.apellidos}".strip())
                db.add(OrdenMecanico(
                    orden_id=orden.id,
                    mecanico_id=mec.id,
                    porcentaje=porcentaje,
                    monto=monto,
                    observaciones="Asignacion demo"
                ))

                if orden.estado == "cancelada" and monto > 0:
                    fecha_base = (orden.fecha or datetime.utcnow()).date()
                    liquidacion = obtener_o_crear_liquidacion(db, mec.id, fecha_base)
                    detalle = LiquidacionMecanicoDetalle(
                        liquidacion_id=liquidacion.id,
                        orden_id=orden.id,
                        porcentaje=porcentaje,
                        base_calculo=total_servicios,
                        monto=monto
                    )
                    db.add(detalle)
                    liquidaciones.add(liquidacion.id)

            for lid in liquidaciones:
                recalcular_liquidacion(db, lid)

            if orden.estado == "cancelada":
                db.add(MovimientoCaja(
                    caja_id=caja.id,
                    tipo="ingreso",
                    concepto=f"Ingreso por orden {orden.id}",
                    monto=total,
                    motivo="Orden cancelada",
                    orden_id=orden.id,
                    usuario="admin"
                ))

                proveedores_texto = ", ".join(sorted(proveedores_set)) or "Proveedor"
                db.add(MovimientoCaja(
                    caja_id=caja.id,
                    tipo="egreso",
                    concepto=f"Pago pendiente proveedor {proveedores_texto} orden {orden.id}",
                    monto=total_proveedor,
                    motivo="Provision proveedores",
                    orden_id=orden.id,
                    usuario="admin"
                ))

                if total_mecanicos > 0:
                    nombres_unicos = ", ".join(sorted(set(nombres_mecanicos))) or "Tecnico"
                    db.add(MovimientoCaja(
                        caja_id=caja.id,
                        tipo="egreso",
                        concepto=f"Pago pendiente tecnico {nombres_unicos} orden {orden.id}",
                        monto=total_mecanicos,
                        motivo="Provision tecnicos",
                        orden_id=orden.id,
                        usuario="admin"
                    ))

        db.add(MovimientoCaja(
            caja_id=caja.id,
            tipo="ingreso",
            concepto="Ingreso manual",
            monto=250000,
            motivo="Ingreso de prueba",
            usuario="admin"
        ))

        db.add(MovimientoCaja(
            caja_id=caja.id,
            tipo="egreso",
            concepto="Gasto operativo",
            monto=120000,
            motivo="Pago de servicios",
            usuario="admin"
        ))

        proveedores_pagados = random.sample(proveedores, 2)
        for prov in proveedores_pagados:
            pago = 50000
            db.add(MovimientoProveedor(
                proveedor_id=prov.id,
                orden_id=None,
                item_id=None,
                tipo="pago",
                cantidad=None,
                valor_unitario=None,
                subtotal=pago,
                motivo="Pago parcial",
                usuario="admin"
            ))
            db.add(MovimientoCaja(
                caja_id=caja.id,
                tipo="egreso",
                concepto=f"Pago proveedor {prov.nombre}",
                monto=pago,
                motivo="Pago parcial",
                proveedor_id=prov.id,
                usuario="admin"
            ))

        liquidaciones = db.query(LiquidacionMecanico).filter(
            LiquidacionMecanico.estado == "pendiente"
        ).all()
        for liq in liquidaciones[:2]:
            liq.estado = "pagado"
            mecanico = db.query(Mecanico).filter(Mecanico.id == liq.mecanico_id).first()
            nombre_mecanico = "Tecnico"
            if mecanico:
                nombre_mecanico = f"{mecanico.nombres} {mecanico.apellidos}".strip()
            db.add(MovimientoCaja(
                caja_id=caja.id,
                tipo="egreso",
                concepto=f"Pago nomina tecnico {nombre_mecanico}",
                monto=liq.total_pagado or 0.0,
                motivo="Pago demo",
                usuario="admin"
            ))

        ingresos = db.query(MovimientoCaja.monto).filter(
            MovimientoCaja.caja_id == caja.id,
            MovimientoCaja.tipo == "ingreso"
        ).all()
        egresos = db.query(MovimientoCaja.monto).filter(
            MovimientoCaja.caja_id == caja.id,
            MovimientoCaja.tipo == "egreso"
        ).all()
        caja.saldo_final = caja.saldo_inicial + sum([i[0] for i in ingresos]) - sum([e[0] for e in egresos])

        db.commit()
        print("Datos de prueba cargados.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
