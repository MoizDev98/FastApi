# app/routes/rol_routes.py
from fastapi import APIRouter, HTTPException
from config.db_config import get_db_connection
from models.rol_model import Rol, RolCreate, RolUpdate, Module
from controllers import rol_controller as controller

routerRole = APIRouter(prefix="/roles", tags=["Roles"])

@routerRole.get("/modules", response_model=list[Module])
def get_modules():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, state FROM module WHERE state = 1")
    modules = cursor.fetchall()
    conn.close()
    return modules

@routerRole.get("/", response_model=list[Rol])
def get_roles():
    return controller.get_all_roles()

@routerRole.get("/{id}", response_model=Rol)
def get_role(id: int):
    return controller.get_role_by_id(id)

@routerRole.post("/", response_model=dict)
def create_role(rol: RolCreate):
    return controller.create_role(rol)

@routerRole.put("/{id}", response_model=dict)
def update_role(id: int, rol: RolUpdate):
    return controller.update_role(id, rol)

@routerRole.delete("/{id}", response_model=dict)
def delete_role(id: int):
    return controller.delete_role(id)