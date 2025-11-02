from config.db_config import get_db_connection
from fastapi import HTTPException

def get_all_modules():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, description, state FROM module WHERE state = 1")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_module_by_id(id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, description, state FROM module WHERE id = %s AND state = 1", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    return row

def create_module(payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO module (name, description, state) VALUES (%s, %s, 1)", (payload.get('name'), payload.get('description')))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Módulo creado", "id": new_id}

def update_module(id: int, payload: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE module SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND state = 1", (payload.get('name'), payload.get('description'), id))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Módulo actualizado"}

def delete_module(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE module SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Módulo eliminado"}
