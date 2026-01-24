"""
Rutas del detalle de insumos en ordenes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import admin_o_mecanico
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.detalle_almacen import DetalleAlmacen
from backend.app.models.movimiento_almacen import MovimientoAlmacen
from backend.app.models.movimiento_proveedor import MovimientoProveedor
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.schemas.detalle_almacen import DetalleAlmacenCreate, DetalleAlmacenResponse


router = APIRouter(
    prefix="/detalle-almacen",
    tags=["Detalle de Almacen"],
    dependencies=[Depends(admin_o_mecanico)],
)


def _registrar_movimiento_proveedor(
    db: Session,
    item: AlmacenItem,
    orden_id: int,
    tipo: str,
    subtotal: float,
    cantidad: float | None,
    valor_unitario: float | None,
    motivo: str,
    usuario: str | None
):
    if not item.proveedor_id or subtotal <= 0:
        return

    movimiento = MovimientoProveedor(
        proveedor_id=item.proveedor_id,
        orden_id=orden_id,
        item_id=item.id,
        tipo=tipo,
        cantidad=cantidad,
        valor_unitario=valor_unitario,
        subtotal=subtotal,
        motivo=motivo,
        usuario=usuario
    )
    db.add(movimiento)


@router.post("/", response_model=DetalleAlmacenResponse)
def agregar_insumo_a_orden(
    detalle: DetalleAlmacenCreate,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    orden = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == detalle.orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no existe")

    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una orden cerrada. Reabra la orden primero.",
        )

    item = db.query(AlmacenItem).filter(AlmacenItem.id == detalle.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no existe")

    if item.stock_actual < detalle.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    subtotal = item.valor_taller * detalle.cantidad
    costo_proveedor_unitario = item.valor_proveedor or 0.0
    subtotal_proveedor = costo_proveedor_unitario * detalle.cantidad
    margen_subtotal = subtotal - subtotal_proveedor

    nuevo_detalle = DetalleAlmacen(
        orden_id=detalle.orden_id,
        item_id=detalle.item_id,
        proveedor_id=item.proveedor_id,
        cantidad=detalle.cantidad,
        precio_unitario=item.valor_taller,
        subtotal=subtotal,
        costo_proveedor_unitario=costo_proveedor_unitario,
        subtotal_proveedor=subtotal_proveedor,
        margen_subtotal=margen_subtotal,
    )

    item.stock_actual -= detalle.cantidad
    orden.total += subtotal

    movimiento = MovimientoAlmacen(
        tipo="salida",
        cantidad=detalle.cantidad,
        valor_unitario=item.valor_taller,
        observaciones="Consumo en orden",
        item_id=item.id,
        orden_id=orden.id,
    )

    _registrar_movimiento_proveedor(
        db=db,
        item=item,
        orden_id=orden.id,
        tipo="cargo",
        subtotal=subtotal_proveedor,
        cantidad=detalle.cantidad,
        valor_unitario=costo_proveedor_unitario,
        motivo="Consumo en orden",
        usuario=usuario.get("sub")
    )

    db.add(nuevo_detalle)
    db.add(movimiento)
    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle


@router.get("/orden/{orden_id}", response_model=list[DetalleAlmacenResponse])
def listar_insumos_por_orden(orden_id: int, db: Session = Depends(get_db)):
    return db.query(DetalleAlmacen).filter(DetalleAlmacen.orden_id == orden_id).all()


@router.put("/{detalle_id}", response_model=DetalleAlmacenResponse)
def editar_detalle_almacen(
    detalle_id: int,
    cantidad: float,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    detalle = db.query(DetalleAlmacen).filter(DetalleAlmacen.id == detalle_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    orden = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == detalle.orden_id).first()
    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una orden cerrada. Reabra la orden primero.",
        )

    item = db.query(AlmacenItem).filter(AlmacenItem.id == detalle.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no existe")

    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad invalida")

    diferencia = cantidad - detalle.cantidad
    if diferencia > 0 and item.stock_actual < diferencia:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    orden.total -= detalle.subtotal

    detalle.cantidad = cantidad
    detalle.subtotal = detalle.precio_unitario * cantidad
    orden.total += detalle.subtotal

    item.stock_actual -= diferencia

    nuevo_subtotal_proveedor = (item.valor_proveedor or 0.0) * cantidad
    delta_proveedor = nuevo_subtotal_proveedor - detalle.subtotal_proveedor

    detalle.costo_proveedor_unitario = item.valor_proveedor or 0.0
    detalle.subtotal_proveedor = nuevo_subtotal_proveedor
    detalle.margen_subtotal = detalle.subtotal - nuevo_subtotal_proveedor
    detalle.proveedor_id = item.proveedor_id

    if diferencia != 0:
        movimiento = MovimientoAlmacen(
            tipo="ajuste",
            cantidad=abs(diferencia),
            valor_unitario=item.valor_taller,
            observaciones="Ajuste por edicion en orden",
            item_id=item.id,
            orden_id=orden.id,
        )
        db.add(movimiento)

    if item.proveedor_id and delta_proveedor != 0:
        tipo = "ajuste_cargo" if delta_proveedor > 0 else "ajuste_abono"
        _registrar_movimiento_proveedor(
            db=db,
            item=item,
            orden_id=orden.id,
            tipo=tipo,
            subtotal=abs(delta_proveedor),
            cantidad=abs(diferencia) if diferencia != 0 else None,
            valor_unitario=item.valor_proveedor,
            motivo="Ajuste por edicion en orden",
            usuario=usuario.get("sub")
        )

    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{detalle_id}")
def eliminar_detalle_almacen(
    detalle_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(admin_o_mecanico)
):
    detalle = db.query(DetalleAlmacen).filter(DetalleAlmacen.id == detalle_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    orden = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == detalle.orden_id).first()
    if orden.estado == "cerrada":
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una orden cerrada. Reabra la orden primero.",
        )

    item = db.query(AlmacenItem).filter(AlmacenItem.id == detalle.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no existe")

    orden.total -= detalle.subtotal
    item.stock_actual += detalle.cantidad

    movimiento = MovimientoAlmacen(
        tipo="devolucion",
        cantidad=detalle.cantidad,
        valor_unitario=detalle.precio_unitario,
        observaciones="Devolucion por eliminar de orden",
        item_id=item.id,
        orden_id=orden.id,
    )

    if detalle.proveedor_id and detalle.subtotal_proveedor > 0:
        _registrar_movimiento_proveedor(
            db=db,
            item=item,
            orden_id=orden.id,
            tipo="abono",
            subtotal=detalle.subtotal_proveedor,
            cantidad=detalle.cantidad,
            valor_unitario=detalle.costo_proveedor_unitario,
            motivo="Reversion por eliminar insumo",
            usuario=usuario.get("sub")
        )

    db.add(movimiento)
    db.delete(detalle)
    db.commit()

    return {"mensaje": "Insumo eliminado de la orden correctamente"}
