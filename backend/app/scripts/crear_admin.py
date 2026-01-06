"""
Script para crear un usuario administrador inicial.
Se ejecuta UNA sola vez.
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import encriptar_password



def crear_admin():
    # Abrimos sesión con la base de datos
    db: Session = SessionLocal()

    # Verificamos si ya existe el usuario admin
    existe = db.query(Usuario).filter(
        Usuario.username == "admin"
    ).first()

    if existe:
        print("⚠️ El usuario admin ya existe")
        db.close()
        return

    # Creamos el usuario admin
    admin = Usuario(
        username="admin",
        password=encriptar_password("admin123"),
        rol="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("✅ Usuario admin creado correctamente")


if __name__ == "__main__":
    crear_admin()
