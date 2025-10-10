# app/routes/type_document_routes.py
from fastapi import APIRouter, HTTPException
from typing import List
from models.type_document import TypeDocument
import controllers.type_document_controller as controller

router = APIRouter(prefix="/type_documents", tags=["TypeDocuments"])

@router.post("/", response_model=TypeDocument)
def create_type_document(doc: TypeDocument):
    row = controller.create_type_document(doc)
    if not row:
        raise HTTPException(status_code=500, detail="No se pudo crear el tipo de documento")
    return row

@router.get("/", response_model=List[TypeDocument])
def get_type_documents():
    return controller.get_all_type_documents()

@router.get("/{id}", response_model=TypeDocument)
def get_type_document(id: int):
    return controller.get_type_document_by_id(id)

@router.put("/{id}", response_model=TypeDocument)
def update_type_document(id: int, doc: TypeDocument):
    return controller.update_type_document(id, doc)

@router.delete("/{id}")
def delete_type_document(id: int):
    return controller.delete_type_document(id)
