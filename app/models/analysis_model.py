# app/models/analysis_model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PredictionOut(BaseModel):
    id_prediction: int
    id_analysis: int
    id_model: Optional[int] = None
    id_disease: Optional[int] = None
    label: str
    probability: float
    rank: Optional[int] = None

    class Config:
        orm_mode = True


class AnalysisOut(BaseModel):
    id_analysis: int
    id_user: int
    id_image: int
    id_model: Optional[int] = None
    id_disease: Optional[int] = None
    id_user_doctor: Optional[int] = None
    date: Optional[datetime] = None
    status: Optional[str] = None
    result_ia: Optional[str] = None
    confidence: Optional[float] = None
    observation_doctor: Optional[str] = None
    url_image: Optional[str] = None
    id_state_analysis: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    state: int
    predictions: List[PredictionOut] = []

    class Config:
        orm_mode = True
