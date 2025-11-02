from fastapi import APIRouter
import controllers.disease_type_controller as controller

router = APIRouter(prefix="/disease_types", tags=["DiseaseTypes"])


@router.get("/")
def get_disease_types():
    return controller.get_all_disease_types()


@router.get("/{id}")
def get_disease_type(id: int):
    return controller.get_disease_type_by_id(id)


@router.post("/")
def create_disease_type(payload: dict):
    return controller.create_disease_type(payload)


@router.put("/{id}")
def update_disease_type(id: int, payload: dict):
    return controller.update_disease_type(id, payload)


@router.delete("/{id}")
def delete_disease_type(id: int):
    return controller.delete_disease_type(id)
