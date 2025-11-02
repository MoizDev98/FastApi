from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiseaseType(BaseModel):
    id_disease: Optional[int] = None
    name: str
    label_s: str
    description: Optional[str] = None
    severity_level: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    state: Optional[int] = None

    class Config:
        orm_mode = True
