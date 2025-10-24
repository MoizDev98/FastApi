from fastapi import APIRouter
import controllers.auth_controller
from models.login_request import LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(request: LoginRequest):
    return controllers.auth_controller.login(request)
