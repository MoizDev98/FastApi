from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Analysis(BaseModel):
    # Ajustado al esquema real de la BD (db_medical_project.sql)
    id_analysis: Optional[int] = None
    # Alias opcional para compatibilidad con el frontend (el controlador devuelve 'id')
    id: Optional[int] = None

    id_user: Optional[int] = None
    id_disease: Optional[int] = None
    id_user_doctor: Optional[int] = None
    date: Optional[datetime] = None
    # En la BD real la FK es id_state_analysis (-> state_analysis)
    id_state_analysis: Optional[int] = None
    # Compatibilidad: permitir id_state en payloads antiguos
    id_state: Optional[int] = None

    result_ia: Optional[str] = None
    observation_doctor: Optional[str] = None
    url_image: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    state: Optional[int] = None