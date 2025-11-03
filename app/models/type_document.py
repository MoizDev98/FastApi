from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TypeDocument(BaseModel):
    id: Optional[int] = None
    name: str
    # abbreviation may be missing in some existing DB rows; accept None to avoid
    # ResponseValidationError when returning rows that don't have this column set.
    abbreviation: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
