# routes/appointment_routes.py
from fastapi import APIRouter, HTTPException
from typing import List
from models.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
import controllers.appointment_controller as appointment_controller

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentOut)
def create_appointment(appointment: AppointmentCreate):
    row = appointment_controller.create_appointment(appointment)
    if not row:
        raise HTTPException(status_code=500, detail="No se pudo crear la cita")
    return row

@router.get("/", response_model=List[AppointmentOut])
def get_appointments():
    return appointment_controller.get_all_appointments()

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
    ok = appointment_controller.delete_appointment(appointment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return {"message": "Cita eliminada correctamente"}
