# app/routes/analysis_routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from models.analysis import Analysis
import controllers.analysis_controller as controller
from controllers import analysis_ia_controller
from models.analysis_model import AnalysisOut

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# -------- CRUD básico existente --------

@router.post("/")
def create(analysis: Analysis):
    """
    Crea un análisis manual (sin usar la IA).
    Se mantiene por compatibilidad con lo que ya tenías.
    """
    return controller.create_analysis(analysis)


@router.get("/")
def get_all():
    return controller.get_all_analysis()


@router.get("/{analysis_id}")
def get_one(analysis_id: int):
    return controller.get_analysis_by_id(analysis_id)


@router.put("/{analysis_id}")
def update(analysis_id: int, analysis: Analysis):from fastapi import APIRouter, UploadFile, File, Form, HTTPException


router = APIRouter(prefix="/analysis", tags=["Analysis"])


# -------- CRUD básico existente --------

@router.post("/", status_code=201)
def create(analysis: Analysis):
    """
    Crea un análisis manual (sin usar la IA).
    Se mantiene por compatibilidad con lo que ya tenías.
    """
    try:
        return controller.create_analysis(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list)
def get_all():
    """Obtiene todos los análisis"""
    try:
        return controller.get_all_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}")
def get_one(analysis_id: int):
    """Obtiene un análisis por ID"""
    try:
        result = controller.get_analysis_by_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user/{user_id}")
def get_by_user(user_id: int):
    """Devuelve todos los análisis de un paciente concreto"""
    try:
        return controller.get_analysis_by_user(user_id)
    except HTTPException:
        # Re-lanzar si viene de controller
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/{analysis_id}")
def update(analysis_id: int, analysis: Analysis):
    """Actualiza un análisis completo"""
    try:
        result = controller.update_analysis(analysis_id, analysis)
        if not result:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{analysis_id}/observation")
def update_observation(analysis_id: int, payload: dict):
    """
    Actualiza solo la observación del doctor (campo observation_doctor).
    """
    try:
        obs = payload.get("observation_doctor")
        if obs is None or obs == "":
            raise HTTPException(
                status_code=400, 
                detail="observation_doctor es requerido y no puede estar vacío"
            )
        
        result = controller.update_analysis_observation(analysis_id, obs)
        if not result:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{analysis_id}", status_code=204)
def delete(analysis_id: int):
    """Elimina un análisis"""
    try:
        result = controller.delete_analysis(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return {"message": "Análisis eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- NUEVO: endpoint que usa la IA --------

@router.post("/upload-ia", response_model=AnalysisOut, status_code=201)
async def upload_and_analyze_image(
    id_user: int = Form(..., description="ID del usuario/paciente"),
    file: UploadFile = File(..., description="Imagen para analizar"),
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
        # Validar que el archivo existe
        if not file:
            raise HTTPException(status_code=400, detail="No se recibió ningún archivo")
        
        # Validar tipo de contenido
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
            )
        
        # Validar tamaño del archivo (por ejemplo, máximo 10MB)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="El archivo es demasiado grande. Máximo 10MB"
            )
        
        # Resetear el puntero del archivo
        await file.seek(0)
        
        # Validar id_user
        if id_user <= 0:
            raise HTTPException(status_code=400, detail="id_user debe ser mayor a 0")

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
            detail=f"Error al procesar la imagen: {str(e)}"
        )
    return controller.update_analysis(analysis_id, analysis)


@router.patch("/{analysis_id}/observation")
def update_observation(analysis_id: int, payload: dict):
    """
    Actualiza solo la observación del doctor (campo observation_doctor).
    """
    obs = payload.get("observation_doctor") if isinstance(payload, dict) else None
    if obs is None:
        raise HTTPException(status_code=400, detail="observation_doctor es requerido")
    return controller.update_analysis_observation(analysis_id, obs)


@router.delete("/{analysis_id}")
def delete(analysis_id: int):
    return controller.delete_analysis(analysis_id)


# -------- NUEVO: endpoint que usa la IA --------

@router.post("/upload-ia", response_model=AnalysisOut)
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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"El archivo debe ser una imagen. Tipo recibido: {file.content_type}",
        )

    return await analysis_ia_controller.create_analysis_with_ia(
        file=file,
        id_user=id_user,
    )


# @router.get("/user/{user_id}")
# def get_by_user(user_id: int):
#     """Obtiene todos los análisis de un paciente específico"""
#     try:
#         return controller.get_analysis_by_user(user_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

