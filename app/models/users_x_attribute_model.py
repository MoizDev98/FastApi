from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserAttribute(BaseModel):
    id: Optional[int] = None
    id_user: int
    id_attribute: int
    worth: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    state: Optional[int] = None

    class Config:
        orm_mode = True
