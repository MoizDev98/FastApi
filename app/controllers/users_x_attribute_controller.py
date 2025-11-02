from config.db_config import get_db_connection
from fastapi import HTTPException

def get_attributes_for_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT ua.id, ua.id_attribute, a.name as attribute_name, ua.worth FROM users_x_attribute ua JOIN attribute a ON ua.id_attribute = a.id WHERE ua.id_user = %s AND ua.state = 1", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_attribute_to_user(id_user: int, id_attribute: int, worth: str = None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users_x_attribute (id_user, id_attribute, worth, state) VALUES (%s, %s, %s, 1)", (id_user, id_attribute, worth))
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Atributo agregado al usuario", "id": new_id}

def remove_user_attribute(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users_x_attribute SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Atributo de usuario no encontrado")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Atributo de usuario eliminado"}
