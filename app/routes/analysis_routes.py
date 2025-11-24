from fastapi import APIRouter
from models.analysis import Analysis
import controllers.analysis_controller as controller
from pydantic import BaseModel

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


@router.put("/{analysis_id}/status")
def update_status(analysis_id: int, payload: dict):
    """Actualiza el estado de un análisis y envía email al paciente"""
    new_state = payload.get("id_state")
    changed_by = payload.get("changed_by_id", 1)  # ID del doctor/usuario que hace el cambio
    
    if new_state is None:
        return {"error": "id_state is required in payload"}
    
    return controller.update_analysis_status(analysis_id, new_state, changed_by)


@router.post("/upload")
def upload_image(payload: dict):
    """Registra la subida de una imagen de análisis y envía confirmación por email"""
    user_id = payload.get("user_id")
    image_path = payload.get("image_path") or payload.get("url_image", "")
    
    if not user_id:
        return {"error": "user_id is required"}
    
    return controller.upload_analysis_image(user_id, image_path)

