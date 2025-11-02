from fastapi import HTTPException
from config.db_config import get_db_connection
from models.analysis import Analysis

# Crear un nuevo análisis
def create_analysis(analysis: Analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO analysis (id_user, name, description, url_image, result_ia, observation_doctor, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    values = (analysis.id_user, analysis.name, analysis.description, getattr(analysis, 'url_image', None), getattr(analysis, 'result_ia', None), getattr(analysis, 'observation_doctor', None))
    cursor.execute(query, values)
    conn.commit()

    analysis.id = cursor.lastrowid
    cursor.close()
    conn.close()
    return analysis

# Obtener todos los análisis
def get_all_analysis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM analysis")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# Obtener un análisis por ID
def get_analysis_by_id(analysis_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM analysis WHERE id = %s", (analysis_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return result

# Actualizar un análisis
def update_analysis(analysis_id: int, analysis: Analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE analysis
        SET id_user = %s, name = %s, description = %s, url_image = %s, result_ia = %s, observation_doctor = %s, updated_at = NOW()
        WHERE id = %s
    """
    values = (
        analysis.id_user,
        analysis.name,
        analysis.description,
        getattr(analysis, 'url_image', None),
        getattr(analysis, 'result_ia', None),
        getattr(analysis, 'observation_doctor', None),
        analysis_id,
    )
    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
    analysis.id = analysis_id
    return analysis

# Eliminar un análisis
def delete_analysis(analysis_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis WHERE id = %s", (analysis_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Análisis eliminado correctamente"}


def update_analysis_observation(analysis_id: int, observation: str):
    """Actualiza únicamente la observación del doctor para un análisis existente."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE analysis SET observation_doctor = %s, updated_at = NOW() WHERE id = %s", (observation, analysis_id))
        conn.commit()
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM analysis WHERE id = %s", (analysis_id,))
        row = cur2.fetchone()
        cur2.close()
        if not row:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return row
    finally:
        conn.close()
