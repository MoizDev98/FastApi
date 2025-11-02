from config.db_config import get_db_connection
from fastapi import HTTPException

def assign_module_to_role(id_rol: int, id_module: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO module_x_rol (id_rol, id_module, state) VALUES (%s, %s, 1)", (id_rol, id_module))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Asignación creada", "id": new_id}

def remove_assignment(id_rol: int, id_module: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM module_x_rol WHERE id_rol = %s AND id_module = %s", (id_rol, id_module))
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return {"message": "Asignación eliminada"}
