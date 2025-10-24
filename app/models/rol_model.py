# app/models/rol_model.py
from pydantic import BaseModel
from typing import Optional, List

class Module(BaseModel):
    id: int
    name: str
    state: int

    class Config:
        orm_mode = True

class RolBase(BaseModel):
    name: str
    description: Optional[str] = None

class RolCreate(RolBase):
    permisos: Optional[List[int]] = None

class RolUpdate(RolBase):
    permisos: Optional[List[int]] = None

class Rol(RolBase):
    id: int
    state: int
    modules: Optional[List[int]] = None

    class Config:
        orm_mode = True