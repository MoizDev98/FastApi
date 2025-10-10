from pydantic import BaseModel
from datetime import datetime

class Rol(BaseModel):
    id: int | None = None
    name: str
    description: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
