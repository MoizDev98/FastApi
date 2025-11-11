from fastapi import APIRouter
from models.analysis import Analysis
import controllers.analysis_controller as controller

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/")
def create(analysis: Analysis):
    return controller.create_analysis(analysis)

@router.get("/")
def get_all():
    return controller.get_all_analysis()

@router.get("/{analysis_id}")
def get_one(analysis_id: int):
    return controller.get_analysis_by_id(analysis_id)

@router.put("/{analysis_id}")
def update(analysis_id: int, analysis: Analysis):
    return controller.update_analysis(analysis_id, analysis)


@router.patch("/{analysis_id}/observation")
def update_observation(analysis_id: int, payload: dict):
    """Actualiza la observación del doctor (campo observation_doctor)"""
    obs = payload.get("observation_doctor") if isinstance(payload, dict) else None
    if obs is None:
        return {"error": "observation_doctor is required in payload"}
    return controller.update_analysis_observation(analysis_id, obs)

@router.delete("/{analysis_id}")
def delete(analysis_id: int):
    return controller.delete_analysis(analysis_id)

