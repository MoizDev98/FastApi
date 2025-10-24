from fastapi import APIRouter
from models.analysis import Analysis
from controllers import analysis_controller as controller

analysis_router = APIRouter(prefix="/analysis", tags=["Analysis"])

@analysis_router.post("/")
def create(analysis: Analysis):
    return controller.create_analysis(analysis)

@analysis_router.get("/")
def get_all():
    return controller.get_all_analysis()

@analysis_router.get("/{analysis_id}")
def get_one(analysis_id: int):
    return controller.get_analysis_by_id(analysis_id)

@analysis_router.put("/{analysis_id}")
def update(analysis_id: int, analysis: Analysis):
    return controller.update_analysis(analysis_id, analysis)

@analysis_router.delete("/{analysis_id}")
def delete(analysis_id: int):
    return controller.delete_analysis(analysis_id)
