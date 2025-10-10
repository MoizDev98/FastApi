from fastapi import APIRouter, HTTPException
from typing import List
from models.attribute_model import Attribute
import controllers.attribute_controller as controller

router = APIRouter(prefix="/attributes", tags=["Attributes"])

@router.post("/", response_model=Attribute)
def create_attribute(attr: Attribute):
    row = controller.create_attribute(attr)
    if not row:
        raise HTTPException(status_code=500, detail="No se pudo crear el atributo")
    return row

@router.get("/", response_model=List[Attribute])
def get_attributes():
    return controller.get_all_attributes()

@router.get("/{id}", response_model=Attribute)
def get_attribute(id: int):
    return controller.get_attribute_by_id(id)

@router.put("/{id}", response_model=Attribute)
def update_attribute(id: int, attr: Attribute):
    return controller.update_attribute(id, attr)

@router.delete("/{id}")
def delete_attribute(id: int):
    return controller.delete_attribute(id)
