from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Analysis(BaseModel):
    id: Optional[int] = None
    id_user: int
    name: str
    description: Optional[str] = None
    url_image: Optional[str] = None
    result_ia: Optional[str] = None
    observation_doctor: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None