from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, status

# ======================================================
# CONFIGURACIÓN JWT
# ======================================================

SECRET_KEY = "MEDINAUTOS_SUPER_SECRETO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ======================================================
# PASSWORDS
# ======================================================

def encriptar_password(password: str):
    return pwd_context.hash(password)


def verificar_password(password_plano, password_hash):
    return pwd_context.verify(password_plano, password_hash)


# ======================================================
# TOKEN JWT
# ======================================================

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def obtener_usuario_desde_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ======================================================
# DEPENDENCIAS DE SEGURIDAD (ROLES)
# ======================================================

def usuario_autenticado(request: Request):
    """
    Verifica que exista un token válido en la cookie
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )

    payload = obtener_usuario_desde_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    return payload


def solo_admin(
    usuario=Depends(usuario_autenticado)
):
    """
    Permite acceso SOLO a usuarios con rol admin
    """
    if usuario.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return usuario


def admin_o_mecanico(
    usuario=Depends(usuario_autenticado)
):
    """
    Permite acceso a admin o mecánico
    """
    if usuario.get("rol") not in ["admin", "mecanico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return usuario
