from fastapi import APIRouter, Request
from models.user_model import User
from controllers.user_controller import UserController

router = APIRouter(prefix="/users", tags=["Users"])
user_controller = UserController()


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
async def update_user(user_id: int, request: Request):
    """Accept partial update payload (JSON) and forward to controller.
    This avoids strict Pydantic validation for PUT so frontend can send partial fields.
    """
    payload = await request.json()
    return user_controller.update_user(user_id, payload)


@router.delete("/{user_id}")
def delete_user(user_id: int):
    return user_controller.delete_user(user_id)
