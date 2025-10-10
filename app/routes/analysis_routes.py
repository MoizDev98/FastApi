from fastapi import APIRouter
from models.analysis import Analysis
from controllers import analysis_controller as controller

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

@router.delete("/{analysis_id}")
def delete(analysis_id: int):
    return controller.delete_analysis(analysis_id)
