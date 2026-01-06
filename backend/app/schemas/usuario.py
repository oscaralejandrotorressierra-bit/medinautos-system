from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str = "mecanico"


class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str

    class Config:
        from_attributes = True  # reemplaza orm_mode (Pydantic v2)
