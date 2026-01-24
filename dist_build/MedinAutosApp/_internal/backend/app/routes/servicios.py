"""
Rutas del módulo Servicios

Este archivo define todos los endpoints relacionados con los servicios
del taller: listar, crear, actualizar, activar/desactivar y eliminar.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Dependencia para obtener la sesión de base de datos
from backend.app.core.database import get_db

# Modelo SQLAlchemy
from backend.app.models.servicio import Servicio

# Schemas de validación y respuesta
from backend.app.schemas.servicio import (
    ServicioCreateSchema,
    ServicioUpdateSchema,
    ServicioResponseSchema
)

# Router del módulo Servicios
router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"]
)

# ==========================================================
# LISTAR SERVICIOS
# ==========================================================
@router.get("/", response_model=list[ServicioResponseSchema])
def listar_servicios(db: Session = Depends(get_db)):
    """
    Retorna la lista de todos los servicios registrados.

    Por ahora retorna todos.
    Más adelante se puede filtrar solo los activos.
    """
    servicios = db.query(Servicio).all()
    return servicios


# ==========================================================
# OBTENER SERVICIO POR ID
# ==========================================================
@router.get("/{servicio_id}", response_model=ServicioResponseSchema)
def obtener_servicio(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna un servicio por su ID.
    """
    servicio = (
        db.query(Servicio)
        .filter(Servicio.id == servicio_id)
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    return servicio


# ==========================================================
# CREAR SERVICIO
# ==========================================================
@router.post("/", response_model=ServicioResponseSchema)
def crear_servicio(
    data: ServicioCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo servicio en el sistema.

    - Valida que no exista un servicio con el mismo nombre
    - Guarda el servicio en la base de datos
    """

    # Verificar si ya existe un servicio con el mismo nombre
    servicio_existente = (
        db.query(Servicio)
        .filter(Servicio.nombre == data.nombre)
        .first()
    )

    if servicio_existente:
        raise HTTPException(
            status_code=400,
            detail="El servicio ya existe"
        )

    # Crear la instancia del modelo Servicio
    servicio = Servicio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        categoria=data.categoria
    )

    # Guardar en la base de datos
    db.add(servicio)
    db.commit()
    db.refresh(servicio)

    return servicio


# ==========================================================
# ACTUALIZAR SERVICIO
# ==========================================================
@router.put("/{servicio_id}", response_model=ServicioResponseSchema)
def actualizar_servicio(
    servicio_id: int,
    data: ServicioUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Actualiza un servicio existente.

    - Permite actualizar solo los campos enviados
    - También permite activar o desactivar el servicio
    """

    # Buscar el servicio por ID (forma recomendada)
    servicio = (
        db.query(Servicio)
        .filter(Servicio.id == servicio_id)
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    # Actualizar solo los campos enviados en el request
    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(servicio, campo, valor)

    db.commit()
    db.refresh(servicio)

    return servicio


# ==========================================================
# ACTIVAR / DESACTIVAR SERVICIO
# ==========================================================
@router.patch("/{servicio_id}/toggle")
def toggle_servicio(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    """
    Activa o desactiva un servicio sin eliminarlo.
    """

    servicio = (
        db.query(Servicio)
        .filter(Servicio.id == servicio_id)
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    # Cambiar el estado activo/inactivo
    servicio.activo = not servicio.activo
    db.commit()

    return {
        "id": servicio.id,
        "activo": servicio.activo
    }


# ==========================================================
# ELIMINAR SERVICIO (CONTROLADO)
# ==========================================================
@router.delete("/{servicio_id}")
def eliminar_servicio(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un servicio de forma permanente.

    ⚠️ Esta acción es irreversible.
    En el frontend debe ir con confirmación.
    """

    servicio = (
        db.query(Servicio)
        .filter(Servicio.id == servicio_id)
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    db.delete(servicio)
    db.commit()

    return {
        "mensaje": "Servicio eliminado correctamente"
    }
