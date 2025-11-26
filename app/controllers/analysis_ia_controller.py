# app/controllers/analysis_ia_controller.py
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, UploadFile
from PIL import Image
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor, MySQLCursorDict

from config.db_config import get_db_connection
from utils.modelo import predecir_imagen
from models.analysis_model import AnalysisOut, PredictionOut


UPLOAD_DIR = Path("uploads/images")


def _save_image_locally(file: UploadFile) -> Dict[str, Any]:
    """
    Guarda el archivo de imagen en disco y devuelve info básica.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(content)

    pil_image = Image.open(BytesIO(content)).convert("RGB")
    width, height = pil_image.size

    return {
        "pil_image": pil_image,
        "filename": filename,
        "path": str(file_path),
        "width": width,
        "height": height,
        "content_type": file.content_type or "image/jpeg",
    }


def _insert_image_upload(conn: MySQLConnection, id_user: int, info: Dict[str, Any]) -> int:
    """
    Inserta en image_upload y devuelve id_image.
    """
    sql = """
        INSERT INTO image_upload (id_user, filename, url, width, height, 
                                  mime_type, uploaded_at, created_at, updated_at, state)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW(), 1)
    """
    params = (
        id_user,
        info["filename"],
        info["path"],
        info["width"],
        info["height"],
        info["content_type"],
    )
    cur: MySQLCursor = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    image_id = cur.lastrowid
    cur.close()
    return image_id


def _map_disease_id(conn: MySQLConnection, diagnostico: str) -> Optional[int]:
    """
    Intenta mapear el diagnóstico devuelto por la IA a disease_type.id_disease.
    """
    cur: MySQLCursorDict = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_disease
        FROM disease_type
        WHERE state = 1 AND (name = %s OR label_s = %s)
        LIMIT 1
        """,
        (diagnostico, diagnostico),
    )
    row = cur.fetchone()
    cur.close()
    if row:
        return row["id_disease"]
    return None


def _insert_analysis(
    conn: MySQLConnection,
    *,
    id_user: int,
    id_image: int,
    id_model: Optional[int],
    id_disease: Optional[int],
    diagnostico: str,
    confidence: float,
    url_image: str,
) -> int:
    """
    Inserta un registro en analysis y devuelve id_analysis.
    """
    sql = """
        INSERT INTO analysis (
            id_user,
            id_image,
            id_model,
            id_disease,
            id_user_doctor,
            date,
            status,
            result_ia,
            confidence,
            observation_doctor,
            url_image,
            created_at,
            updated_at,
            state,
            id_state_analysis
        )
        VALUES (%s, %s, %s, %s, NULL, NOW(), %s, %s, %s, NULL, %s, NOW(), NOW(), 1, 1)
    """
    params = (
        id_user,
        id_image,
        id_model,
        id_disease,
        "Pending",
        diagnostico,
        confidence,
        url_image,
    )
    cur: MySQLCursor = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    analysis_id = cur.lastrowid
    cur.close()
    return analysis_id


def _insert_prediction(
    conn: MySQLConnection,
    *,
    id_analysis: int,
    id_model: Optional[int],
    id_disease: Optional[int],
    diagnostico: str,
    confidence: float,
    rank: int = 1,
) -> int:
    """
    Inserta en prediction y devuelve id_prediction.
    """
    sql = """
        INSERT INTO prediction (
            id_analysis,
            id_model,
            id_disease,
            label,
            probability,
            rank,
            created_at,
            updated_at,
            state
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
    """
    params = (
        id_analysis,
        id_model,
        id_disease,
        diagnostico,
        confidence,
        rank,
    )
    cur: MySQLCursor = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    prediction_id = cur.lastrowid
    cur.close()
    return prediction_id


def _get_analysis_with_predictions(conn: MySQLConnection, analysis_id: int) -> AnalysisOut:
    """
    Recupera el analysis + sus predictions y lo mapea a AnalysisOut.
    """
    cur: MySQLCursorDict = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            a.id_analysis,
            a.id_user,
            a.id_image,
            a.id_model,
            a.id_disease,
            a.id_user_doctor,
            a.date,
            a.status,
            a.result_ia,
            a.confidence,
            a.observation_doctor,
            a.url_image,
            a.id_state_analysis,
            a.created_at,
            a.updated_at,
            a.state
        FROM analysis AS a
        WHERE a.id_analysis = %s
        """,
        (analysis_id,),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    cur2: MySQLCursorDict = conn.cursor(dictionary=True)
    cur2.execute(
        """
        SELECT
            id_prediction,
            id_analysis,
            id_model,
            id_disease,
            label,
            probability,
            rank
        FROM prediction
        WHERE id_analysis = %s AND state = 1
        ORDER BY rank ASC, id_prediction ASC
        """,
        (analysis_id,),
    )
    pred_rows = cur2.fetchall()
    cur2.close()

    preds: List[PredictionOut] = [
        PredictionOut(
            id_prediction=pr["id_prediction"],
            id_analysis=pr["id_analysis"],
            id_model=pr.get("id_model"),
            id_disease=pr.get("id_disease"),
            label=pr["label"],
            probability=float(pr["probability"]),
            rank=pr.get("rank"),
        )
        for pr in pred_rows
    ]

    analysis_out = AnalysisOut(
        id_analysis=row["id_analysis"],
        id_user=row["id_user"],
        id_image=row["id_image"],
        id_model=row.get("id_model"),
        id_disease=row.get("id_disease"),
        id_user_doctor=row.get("id_user_doctor"),
        date=row.get("date"),
        status=row.get("status"),
        result_ia=row.get("result_ia"),
        confidence=float(row["confidence"]) if row.get("confidence") is not None else None,
        observation_doctor=row.get("observation_doctor"),
        url_image=row.get("url_image"),
        id_state_analysis=row.get("id_state_analysis"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        state=row["state"],
        predictions=preds,
    )
    return analysis_out


async def create_analysis_with_ia(
    file: UploadFile,
    id_user: int,
    id_model: Optional[int] = 1,
) -> AnalysisOut:
    """
    Flujo completo:
        - Guarda la imagen en disco y en image_upload
        - Llama a la IA
        - Mapea el diagnóstico a disease_type
        - Crea analysis + prediction
        - Devuelve AnalysisOut con las predicciones
    """
    conn: MySQLConnection = get_db_connection()
    try:
        # 1) Guardar imagen
        info = _save_image_locally(file)

        # 2) Registrar en image_upload
        image_id = _insert_image_upload(conn, id_user=id_user, info=info)

        # 3) Ejecutar IA
        diagnostico, prob = predecir_imagen(info["pil_image"])
        confidence = float(prob)

        # 4) Buscar id_disease
        disease_id = _map_disease_id(conn, diagnostico)

        # 5) Registrar analysis
        analysis_id = _insert_analysis(
            conn,
            id_user=id_user,
            id_image=image_id,
            id_model=id_model,
            id_disease=disease_id,
            diagnostico=diagnostico,
            confidence=confidence,
            url_image=info["path"],
        )

        # 6) Registrar prediction (top-1)
        _insert_prediction(
            conn,
            id_analysis=analysis_id,
            id_model=id_model,
            id_disease=disease_id,
            diagnostico=diagnostico,
            confidence=confidence,
            rank=1,
        )

        # 7) Volver a leer todo y devolverlo bonito
        return _get_analysis_with_predictions(conn, analysis_id)
    finally:
        conn.close()
