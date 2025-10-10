from fastapi import APIRouter
from models.rol_model import Rol
from controllers import rol_controller as controller

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/")
def get_roles():
    return controller.get_all_roles()

@router.get("/{id}")
def get_role(id: int):
    return controller.get_role_by_id(id)

@router.post("/")
def create_role(rol: Rol):
    return controller.create_role(rol)

@router.put("/{id}")
def update_role(id: int, rol: Rol):
    return controller.update_role(id, rol)

@router.delete("/{id}")
def delete_role(id: int):
    return controller.delete_role(id)
