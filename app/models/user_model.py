from pydantic import BaseModel

class User(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    edad: int
    usuario: str
    contrasena: str