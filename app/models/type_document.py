from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TypeDocument(BaseModel):
    id: Optional[int] = None
    name: str
    abbreviation: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
