from fastapi import HTTPException
# app/controllers/rol_controller.py
from config.db_config import get_db_connection
from models.rol_model import Rol, Module

def get_all_roles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener todos los roles
    cursor.execute("SELECT id, name, description, state FROM rol WHERE state = 1")
    roles = cursor.fetchall()
    
    # Obtener módulos para cada rol
    for role in roles:
        cursor.execute(
            "SELECT m.id, m.name FROM module m "
            "JOIN module_x_rol mx ON m.id = mx.id_module "
            "WHERE mx.id_rol = %s AND mx.state = 1",
            (role['id'],)
        )
        modules = cursor.fetchall()
        role['modules'] = [m['id'] for m in modules]  # Añadir array de IDs de módulos
    
    conn.close()
    return roles

def get_role_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, state FROM rol WHERE id = %s AND state = 1", (id,))
    role = cursor.fetchone()
    if not role:
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    cursor.execute(
        "SELECT m.id, m.name FROM module m "
        "JOIN module_x_rol mx ON m.id = mx.id_module "
        "WHERE mx.id_rol = %s AND mx.state = 1",
        (id,)
    )
    modules = cursor.fetchall()
    role['modules'] = [m['id'] for m in modules]
    
    conn.close()
    return role

def create_role(rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rol (name, description, state) VALUES (%s, %s, 1)",
        (rol.name, rol.description)
    )
    role_id = cursor.lastrowid
    
    if hasattr(rol, 'permisos') and rol.permisos:
        for module_id in rol.permisos:
            cursor.execute(
                "INSERT INTO module_x_rol (id_rol, id_module, state) VALUES (%s, %s, 1)",
                (role_id, module_id)
            )
    
    conn.commit()
    conn.close()
    return {"message": "Rol creado exitosamente", "id": role_id}

def update_role(id: int, rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Debug: mostrar payload recibido para facilitar diagnóstico
    try:
        print("▶ update_role called for id=", id)
        # 'rol' puede ser un Pydantic model; intentamos mostrar su dict si existe
        try:
            payload = rol.dict()
        except Exception:
            payload = dict(rol)
        print("▶ payload:", payload)
    except Exception:
        pass
    cursor.execute(
        "UPDATE rol SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND state = 1",
        (rol.name, rol.description, id)
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    # Eliminar permisos existentes
    cursor.execute("DELETE FROM module_x_rol WHERE id_rol = %s", (id,))
    
    # Insertar nuevos permisos
    if hasattr(rol, 'permisos') and rol.permisos:
        for module_id in rol.permisos:
            cursor.execute(
                "INSERT INTO module_x_rol (id_rol, id_module, state) VALUES (%s, %s, 1)",
                (id, module_id)
            )
    
    conn.commit()
    conn.close()
    return {"message": "Rol actualizado exitosamente"}

def delete_role(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE rol SET state = 0, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    cursor.execute("UPDATE module_x_rol SET state = 0 WHERE id_rol = %s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Rol eliminado exitosamente"}