"""
Rutas del modulo Almacen
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import solo_admin
from backend.app.models.almacen_item import AlmacenItem
from backend.app.models.movimiento_almacen import MovimientoAlmacen
from backend.app.models.proveedor import Proveedor
from backend.app.schemas.almacen_item import (
    AlmacenItemCreateSchema,
    AlmacenItemUpdateSchema,
    AlmacenItemResponseSchema,
    MovimientoEntradaSchema,
)
from backend.app.schemas.movimiento_almacen import MovimientoAlmacenResponseSchema
from backend.app.schemas.proveedor import (
    ProveedorCreateSchema,
    ProveedorUpdateSchema,
    ProveedorResponseSchema,
)


router = APIRouter(
    prefix="/almacen",
    tags=["Almacen"],
    dependencies=[Depends(solo_admin)],
)


@router.get("/items", response_model=list[AlmacenItemResponseSchema])
def listar_items(db: Session = Depends(get_db)):
    return db.query(AlmacenItem).all()


@router.get("/items/{item_id}", response_model=AlmacenItemResponseSchema)
def obtener_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(AlmacenItem).filter(AlmacenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return item


@router.post("/items", response_model=AlmacenItemResponseSchema)
def crear_item(data: AlmacenItemCreateSchema, db: Session = Depends(get_db)):
    existente = db.query(AlmacenItem).filter(AlmacenItem.nombre == data.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="El insumo ya existe")

    item = AlmacenItem(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=AlmacenItemResponseSchema)
def actualizar_item(item_id: int, data: AlmacenItemUpdateSchema, db: Session = Depends(get_db)):
    item = db.query(AlmacenItem).filter(AlmacenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(item, campo, valor)

    db.commit()
    db.refresh(item)
    return item


@router.patch("/items/{item_id}/toggle")
def toggle_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(AlmacenItem).filter(AlmacenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")

    item.activo = not item.activo
    db.commit()
    return {"id": item.id, "activo": item.activo}


@router.delete("/items/{item_id}")
def eliminar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(AlmacenItem).filter(AlmacenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")

    db.delete(item)
    db.commit()
    return {"mensaje": "Insumo eliminado correctamente"}


@router.post("/items/{item_id}/entrada", response_model=MovimientoAlmacenResponseSchema)
def registrar_entrada(item_id: int, data: MovimientoEntradaSchema, db: Session = Depends(get_db)):
    item = db.query(AlmacenItem).filter(AlmacenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")

    if data.proveedor_id:
        proveedor = db.query(Proveedor).filter(Proveedor.id == data.proveedor_id).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    item.stock_actual += data.cantidad
    if data.valor_unitario is not None:
        item.valor_proveedor = data.valor_unitario

    movimiento = MovimientoAlmacen(
        tipo="entrada",
        cantidad=data.cantidad,
        valor_unitario=data.valor_unitario,
        observaciones=data.observaciones,
        item_id=item.id,
        proveedor_id=data.proveedor_id,
    )

    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.get("/movimientos", response_model=list[MovimientoAlmacenResponseSchema])
def listar_movimientos(item_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(MovimientoAlmacen)
    if item_id:
        query = query.filter(MovimientoAlmacen.item_id == item_id)
    return query.order_by(MovimientoAlmacen.fecha.desc()).all()


@router.get("/proveedores", response_model=list[ProveedorResponseSchema])
def listar_proveedores(db: Session = Depends(get_db)):
    return db.query(Proveedor).all()


@router.get("/proveedores/{proveedor_id}", response_model=ProveedorResponseSchema)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.post("/proveedores", response_model=ProveedorResponseSchema)
def crear_proveedor(data: ProveedorCreateSchema, db: Session = Depends(get_db)):
    existente = db.query(Proveedor).filter(Proveedor.nombre == data.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="El proveedor ya existe")

    proveedor = Proveedor(**data.dict())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.put("/proveedores/{proveedor_id}", response_model=ProveedorResponseSchema)
def actualizar_proveedor(
    proveedor_id: int,
    data: ProveedorUpdateSchema,
    db: Session = Depends(get_db),
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(proveedor, campo, valor)

    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete("/proveedores/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db.delete(proveedor)
    db.commit()
    return {"mensaje": "Proveedor eliminado correctamente"}
