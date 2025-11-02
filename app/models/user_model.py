from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class User(BaseModel):
    id: Optional[int] = None
    user_name: str
    password: str
    full_name: str
    last_name: Optional[str] = None
    email: str
    date_birth: Optional[date] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    # specialty: Optional[str] = None
    id_type_document: Optional[int] = None
    num_document: Optional[str] = None
    id_rol: Optional[int] = None
    genero: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
