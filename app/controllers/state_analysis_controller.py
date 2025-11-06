from config.db_config import get_db_connection
from fastapi import HTTPException


def get_all_states():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_state_analysis, state_name, state FROM state_analysis WHERE state = 1")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_state_by_id(id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id_state_analysis, state_name, state FROM state_analysis WHERE id_state_analysis = %s AND state = 1",
        (id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Estado de análisis no encontrado")
    return row


def create_state(payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO state_analysis (state_name, state) VALUES (%s, 1)",
        (payload.get("state_name"),),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado de análisis creado", "id": new_id}


def update_state(id: int, payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE state_analysis SET state_name = %s, updated_at = CURRENT_TIMESTAMP WHERE id_state_analysis = %s AND state = 1",
        (payload.get("state_name"), id),
    )
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Estado de análisis no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado de análisis actualizado"}


def delete_state(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE state_analysis SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id_state_analysis = %s",
        (id,),
    )
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Estado de análisis no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado de análisis eliminado"}
