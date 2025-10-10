from fastapi import HTTPException
from database import get_db_connection
from models.rol_model import Rol
from datetime import datetime

def get_all_roles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rol")
    roles = cursor.fetchall()
    conn.close()
    return roles

def get_role_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rol WHERE id = %s", (id,))
    rol = cursor.fetchone()
    conn.close()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

def create_role(rol: Rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO rol (name, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
    """, (rol.name, rol.description, now, now))
    conn.commit()
    conn.close()
    return {"message": "Rol creado correctamente"}

def update_role(id: int, rol: Rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rol WHERE id = %s", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    now = datetime.now()
    cursor.execute("""
        UPDATE rol SET name = %s, description = %s, updated_at = %s WHERE id = %s
    """, (rol.name, rol.description, now, id))
    conn.commit()
    conn.close()
    return {"message": "Rol actualizado correctamente"}

def delete_role(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rol WHERE id = %s", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    cursor.execute("DELETE FROM rol WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Rol eliminado correctamente"}
