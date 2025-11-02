from fastapi import APIRouter, HTTPException
import controllers.users_x_attribute_controller as controller

router = APIRouter(prefix="/users_x_attribute", tags=["UsersXAttribute"])


@router.get("/user/{user_id}")
def get_attributes_for_user(user_id: int):
    return controller.get_attributes_for_user(user_id)


@router.post("/")
def add_attribute_to_user(payload: dict):
    id_user = payload.get('id_user')
    id_attribute = payload.get('id_attribute')
    worth = payload.get('worth')
    if not id_user or not id_attribute:
        raise HTTPException(status_code=400, detail="id_user y id_attribute requeridos")
    return controller.add_attribute_to_user(id_user, id_attribute, worth)


@router.delete("/{id}")
def remove_user_attribute(id: int):
    return controller.remove_user_attribute(id)
