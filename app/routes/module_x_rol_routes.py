from fastapi import APIRouter, HTTPException
import controllers.module_x_rol_controller as controller

router = APIRouter(prefix="/module_x_rol", tags=["ModuleXRole"])


@router.post("/")
def assign_module_to_role(payload: dict):
    id_rol = payload.get('id_rol')
    id_module = payload.get('id_module')
    if not id_rol or not id_module:
        raise HTTPException(status_code=400, detail="id_rol e id_module requeridos")
    return controller.assign_module_to_role(id_rol, id_module)


@router.delete("/")
def remove_assignment(payload: dict):
    id_rol = payload.get('id_rol')
    id_module = payload.get('id_module')
    if not id_rol or not id_module:
        raise HTTPException(status_code=400, detail="id_rol e id_module requeridos")
    return controller.remove_assignment(id_rol, id_module)
