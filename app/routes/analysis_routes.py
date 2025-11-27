# app/routes/analysis_routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from models.analysis import Analysis
from models.analysis_model import AnalysisOut

# IMPORTAMOS EL CONTROLADOR USANDO EL ESTILO ORIGINAL DEL PROYECTO
import controllers.analysis_controller as controller
from controllers import analysis_ia_controller

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# ------------------- CRUD BÁSICO -------------------

@router.post("/", status_code=201)
def create(analysis: Analysis):
    """Crea un análisis manual (sin IA)."""
    try:
        return controller.create_analysis(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list)
def get_all():
    """Obtiene todos los análisis."""
    try:
        return controller.get_all_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}")
def get_one(analysis_id: int):
    """Obtiene un análisis por ID."""
    try:
        return controller.get_analysis_by_id(analysis_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- NUEVO: HISTORIAL POR PACIENTE -------------------

@router.get("/user/{user_id}")
def get_by_user(user_id: int):
    """Devuelve todos los análisis de un paciente concreto (id_user)."""
    try:
        return controller.get_analysis_by_user(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- UPDATE COMPLETO -------------------

@router.put("/{analysis_id}")
def update(analysis_id: int, analysis: Analysis):
    """Actualiza un análisis completo."""
    try:
        return controller.update_analysis(analysis_id, analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- PATCH SOLO OBSERVACIÓN -------------------

@router.patch("/{analysis_id}/observation")
def update_observation(analysis_id: int, payload: dict):
    """Actualiza solo la observación del doctor (observation_doctor)."""
    obs = payload.get("observation_doctor") if isinstance(payload, dict) else None
    if not obs:
        raise HTTPException(
            status_code=400,
            detail="observation_doctor es requerido y no puede estar vacío",
        )

    try:
        return controller.update_analysis_observation(analysis_id, obs)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- DELETE -------------------

@router.delete("/{analysis_id}", status_code=204)
def delete(analysis_id: int):
    """Elimina un análisis."""
    try:
        controller.delete_analysis(analysis_id)
        return {"message": "Análisis eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- IA: SUBIR Y ANALIZAR IMAGEN -------------------

@router.post("/upload-ia", response_model=AnalysisOut, status_code=201)
async def upload_and_analyze_image(
    id_user: int = Form(...),
    file: UploadFile = File(...),
):
    """
    Endpoint que usa la IA:

    - Recibe un archivo de imagen y el id del paciente (id_user)
    - Guarda la imagen en la tabla image_upload
    - Ejecuta el modelo de IA sobre la imagen
    - Crea registros en analysis y prediction
    - Devuelve AnalysisOut (análisis + predicciones)
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No se recibió ningún archivo")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
            )

        # Llamar al controlador de IA
        return await analysis_ia_controller.create_analysis_with_ia(
            file=file,
            id_user=id_user,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}",
        )
