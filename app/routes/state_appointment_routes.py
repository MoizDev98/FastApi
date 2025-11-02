from fastapi import APIRouter
import controllers.state_appointment_controller as controller

router = APIRouter(prefix="/state_appointments", tags=["StateAppointments"])


@router.get("/")
def get_states():
    return controller.get_all_states()


@router.get("/{id}")
def get_state(id: int):
    return controller.get_state_by_id(id)


@router.post("/")
def create_state(payload: dict):
    return controller.create_state(payload)


@router.put("/{id}")
def update_state(id: int, payload: dict):
    return controller.update_state(id, payload)


@router.delete("/{id}")
def delete_state(id: int):
    return controller.delete_state(id)
