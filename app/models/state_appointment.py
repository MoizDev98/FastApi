from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StateAppointment(BaseModel):
    id_state: Optional[int] = None
    state_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    state: Optional[int] = None

    class Config:
        orm_mode = True
