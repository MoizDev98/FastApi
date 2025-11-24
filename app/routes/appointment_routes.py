# routes/appointment_routes.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
import controllers.appointment_controller as appointment_controller
from datetime import datetime

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentOut)
def create_appointment(appointment: AppointmentCreate):
    row = appointment_controller.create_appointment(appointment)
    if not row:
        raise HTTPException(status_code=500, detail="No se pudo crear la cita")
    return row

@router.get("/", response_model=List[AppointmentOut])
def get_appointments(
    doctor_id: Optional[int] = Query(None, description="Filtrar por id del doctor (id_user_doctor)"),
    state: Optional[int] = Query(None, description="Filtrar por id del estado de cita"),
    date_from: Optional[datetime] = Query(None, description="Fecha/hora desde (inclusive)"),
    date_to: Optional[datetime] = Query(None, description="Fecha/hora hasta (inclusive)"),
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=1000),
):
    offset = (page - 1) * size
    return appointment_controller.get_filtered_appointments(
        doctor_id=doctor_id,
        state=state,
        date_from=date_from,
        date_to=date_to,
        limit=size,
        offset=offset,
    )

from config.security import get_current_user

@router.get("/mine", response_model=List[AppointmentOut])
def get_my_appointments(
    state: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    doctor_id = current_user.get("id")
    if not doctor_id:
        raise HTTPException(status_code=401, detail="No autenticado")
    offset = (page - 1) * size
    return appointment_controller.get_filtered_appointments(
        doctor_id=doctor_id,
        state=state,
        date_from=date_from,
        date_to=date_to,
        limit=size,
        offset=offset,
    )

@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int):
    row = appointment_controller.get_appointment_by_id(appointment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return row

@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, appointment: AppointmentUpdate):
    updated = appointment_controller.update_appointment(appointment_id, appointment)
    if updated is None:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    if not updated:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return updated

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int):
    return appointment_controller.delete_appointment(appointment_id)


@router.put("/{appointment_id}/status")
def update_status(appointment_id: int, payload: dict):
    """Actualiza el estado de una cita y envía email al paciente"""
    new_state = payload.get("id_state")
    changed_by = payload.get("changed_by_id", 1)  # ID del usuario que hace el cambio
    
    if new_state is None:
        return {"error": "id_state is required in payload"}
    
    return appointment_controller.update_appointment_status(appointment_id, new_state, changed_by)
    if not ok:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return {"message": "Cita eliminada correctamente"}

# (Eliminada la segunda definición duplicada de /mine)
