from config.db_config import get_db_connection
from fastapi import HTTPException

def get_all_states():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_state, state_name, state FROM state_appointment WHERE state = 1")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_state_by_id(id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_state, state_name, state FROM state_appointment WHERE id_state = %s AND state = 1", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Estado de cita no encontrado")
    return row

def create_state(payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO state_appointment (state_name, state) VALUES (%s, 1)", (payload.get('state_name'),))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado creado", "id": new_id}

def update_state(id: int, payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE state_appointment SET state_name = %s, updated_at = CURRENT_TIMESTAMP WHERE id_state = %s AND state = 1", (payload.get('state_name'), id))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado actualizado"}

def delete_state(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE state_appointment SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id_state = %s", (id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Estado eliminado"}
