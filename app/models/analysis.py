from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Analysis(BaseModel):
    id: Optional[int] = None
    id_user: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None