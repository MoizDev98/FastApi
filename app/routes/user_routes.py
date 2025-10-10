from fastapi import APIRouter
from models.user_model import User
from controllers import user_controller

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_all_users():
    return user_controller.get_all_users()

@router.get("/{user_id}")
def get_user_by_id(user_id: int):
    return user_controller.get_user_by_id(user_id)

@router.post("/")
def create_user(user: User):
    return user_controller.create_user(user)

@router.put("/{user_id}")
def update_user(user_id: int, user: User):
    return user_controller.update_user(user_id, user)

@router.delete("/{user_id}")
def delete_user(user_id: int):
    return user_controller.delete_user(user_id)
