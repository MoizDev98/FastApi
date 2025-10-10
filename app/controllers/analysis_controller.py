from fastapi import HTTPException
from app.database import get_db_connection
from models.analysis import Analysis

# Crear un nuevo análisis
def create_analysis(analysis: Analysis):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO analysis (id_user, name, description, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
    """
    values = (analysis.id_user, analysis.name, analysis.description)
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
        SET id_user = %s, name = %s, description = %s, updated_at = NOW()
        WHERE id = %s
    """
    values = (analysis.id_user, analysis.name, analysis.description, analysis_id)
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
