from config.db_config import get_db_connection
from fastapi import HTTPException

def get_all_disease_types():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_disease, name, label_s, description, severity_level, state FROM disease_type WHERE state = 1")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_disease_type_by_id(id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_disease, name, label_s, description, severity_level, state FROM disease_type WHERE id_disease = %s AND state = 1", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Tipo de enfermedad no encontrado")
    return row

def create_disease_type(payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO disease_type (name, label_s, description, severity_level, state) VALUES (%s, %s, %s, %s, 1)", (payload.get('name'), payload.get('label_s'), payload.get('description'), payload.get('severity_level')))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Tipo de enfermedad creado", "id": new_id}

def update_disease_type(id: int, payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE disease_type SET name = %s, label_s = %s, description = %s, severity_level = %s, updated_at = CURRENT_TIMESTAMP WHERE id_disease = %s AND state = 1", (payload.get('name'), payload.get('label_s'), payload.get('description'), payload.get('severity_level'), id))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Tipo de enfermedad no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Tipo de enfermedad actualizado"}

def delete_disease_type(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE disease_type SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id_disease = %s", (id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Tipo de enfermedad no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Tipo de enfermedad eliminado"}
