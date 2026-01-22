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
from backend.app.models.orden_trabajo import OrdenTrabajo
from backend.app.schemas.detalle_almacen import DetalleAlmacenCreate, DetalleAlmacenResponse


router = APIRouter(
    prefix="/detalle-almacen",
    tags=["Detalle de Almacen"],
    dependencies=[Depends(admin_o_mecanico)],
)


@router.post("/", response_model=DetalleAlmacenResponse)
def agregar_insumo_a_orden(
    detalle: DetalleAlmacenCreate,
    db: Session = Depends(get_db),
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
    nuevo_detalle = DetalleAlmacen(
        orden_id=detalle.orden_id,
        item_id=detalle.item_id,
        cantidad=detalle.cantidad,
        precio_unitario=item.valor_taller,
        subtotal=subtotal,
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

    db.add(nuevo_detalle)
    db.add(movimiento)
    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle


@router.get("/orden/{orden_id}", response_model=list[DetalleAlmacenResponse])
def listar_insumos_por_orden(orden_id: int, db: Session = Depends(get_db)):
    return db.query(DetalleAlmacen).filter(DetalleAlmacen.orden_id == orden_id).all()


@router.put("/{detalle_id}", response_model=DetalleAlmacenResponse)
def editar_detalle_almacen(detalle_id: int, cantidad: float, db: Session = Depends(get_db)):
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

    db.commit()
    db.refresh(detalle)
    return detalle


@router.delete("/{detalle_id}")
def eliminar_detalle_almacen(detalle_id: int, db: Session = Depends(get_db)):
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

    db.add(movimiento)
    db.delete(detalle)
    db.commit()

    return {"mensaje": "Insumo eliminado de la orden correctamente"}
