"""
Rutas del modulo Categorias de Servicio
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.categoria_servicio import CategoriaServicio
from backend.app.schemas.categoria_servicio import (
    CategoriaServicioCreateSchema,
    CategoriaServicioUpdateSchema,
    CategoriaServicioResponseSchema
)

router = APIRouter(
    prefix="/categorias-servicio",
    tags=["Categorias Servicio"]
)


@router.get("/", response_model=list[CategoriaServicioResponseSchema])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaServicio).all()


@router.get("/{categoria_id}", response_model=CategoriaServicioResponseSchema)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = (
        db.query(CategoriaServicio)
        .filter(CategoriaServicio.id == categoria_id)
        .first()
    )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    return categoria


@router.post("/", response_model=CategoriaServicioResponseSchema)
def crear_categoria(
    data: CategoriaServicioCreateSchema,
    db: Session = Depends(get_db)
):
    categoria_existente = (
        db.query(CategoriaServicio)
        .filter(CategoriaServicio.nombre == data.nombre)
        .first()
    )

    if categoria_existente:
        raise HTTPException(status_code=400, detail="La categoria ya existe")

    categoria = CategoriaServicio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        activo=data.activo if data.activo is not None else True
    )

    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaServicioResponseSchema)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaServicioUpdateSchema,
    db: Session = Depends(get_db)
):
    categoria = (
        db.query(CategoriaServicio)
        .filter(CategoriaServicio.id == categoria_id)
        .first()
    )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)
    return categoria


@router.patch("/{categoria_id}/toggle")
def toggle_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = (
        db.query(CategoriaServicio)
        .filter(CategoriaServicio.id == categoria_id)
        .first()
    )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    categoria.activo = not categoria.activo
    db.commit()

    return {"id": categoria.id, "activo": categoria.activo}


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = (
        db.query(CategoriaServicio)
        .filter(CategoriaServicio.id == categoria_id)
        .first()
    )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    db.delete(categoria)
    db.commit()

    return {"mensaje": "Categoria eliminada correctamente"}
