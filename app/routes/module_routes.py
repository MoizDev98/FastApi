from fastapi import APIRouter
import controllers.module_controller as controller
from models.rol_model import Module

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get("/", response_model=list[Module])
def get_modules():
    return controller.get_all_modules()


@router.get("/{id}", response_model=Module)
def get_module(id: int):
    return controller.get_module_by_id(id)


@router.post("/")
def create_module(payload: dict):
    return controller.create_module(payload)


@router.put("/{id}")
def update_module(id: int, payload: dict):
    return controller.update_module(id, payload)


@router.delete("/{id}")
def delete_module(id: int):
    return controller.delete_module(id)
