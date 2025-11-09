from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    id_user: int
    id_user_doctor: int | None = None
    appointment_date: datetime
    id_state: int

class AppointmentUpdate(BaseModel):
    id_user: Optional[int] = None
    id_user_doctor: Optional[int] = None
    appointment_date: Optional[datetime] = None
    id_state: Optional[int] = None

class AppointmentOut(BaseModel):
    id_appointment: int
    id_user: int
    id_user_doctor: Optional[int] = None
    appointment_date: Optional[datetime] = None
    id_state: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
