from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Attribute(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
