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
    cursor = conn.cursor(dictionary=True)
    
    # Verificar si el nombre del rol ya existe
    cursor.execute(
        "SELECT id FROM rol WHERE name = %s AND state = 1",
        (rol.name,)
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail=f"El rol '{rol.name}' ya existe")
    
    # Crear el rol
    cursor.execute(
        "INSERT INTO rol (name, description, state, created_at, updated_at) "
        "VALUES (%s, %s, 1, NOW(), NOW())",
        (rol.name, rol.description or '')
    )
    role_id = cursor.lastrowid
    
    # Asignar módulos si se proporcionaron
    if hasattr(rol, 'permisos') and rol.permisos:
        for module_id in rol.permisos:
            # Verificar que el módulo existe
            cursor.execute(
                "SELECT id FROM module WHERE id = %s AND state = 1",
                (module_id,)
            )
            if cursor.fetchone():
                cursor.execute(
                    "INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) "
                    "VALUES (%s, %s, 1, NOW(), NOW())",
                    (role_id, module_id)
                )
    
    conn.commit()
    conn.close()
    return {"message": "Rol creado exitosamente", "id": role_id}

def update_role(id: int, rol):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar que el rol existe
    cursor.execute(
        "SELECT id, name FROM rol WHERE id = %s AND state = 1",
        (id,)
    )
    existing_role = cursor.fetchone()
    if not existing_role:
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    # Verificar si hay otro rol con el mismo nombre (excluyendo el actual)
    cursor.execute(
        "SELECT id FROM rol WHERE name = %s AND id != %s AND state = 1",
        (rol.name, id)
    )
    duplicate = cursor.fetchone()
    if duplicate:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Ya existe otro rol con el nombre '{rol.name}'")
    
    # Actualizar el rol
    cursor.execute(
        "UPDATE rol SET name = %s, description = %s, updated_at = NOW() "
        "WHERE id = %s AND state = 1",
        (rol.name, rol.description or '', id)
    )
    
    # Eliminar permisos existentes (soft delete)
    cursor.execute(
        "UPDATE module_x_rol SET state = 0, updated_at = NOW() WHERE id_rol = %s",
        (id,)
    )
    
    # Insertar nuevos permisos
    if hasattr(rol, 'permisos') and rol.permisos:
        for module_id in rol.permisos:
            # Verificar que el módulo existe
            cursor.execute(
                "SELECT id FROM module WHERE id = %s AND state = 1",
                (module_id,)
            )
            if cursor.fetchone():
                cursor.execute(
                    "INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) "
                    "VALUES (%s, %s, 1, NOW(), NOW())",
                    (id, module_id)
                )
    
    conn.commit()
    conn.close()
    return {"message": "Rol actualizado exitosamente"}

def delete_role(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar que el rol existe y no es un rol base protegido
    cursor.execute(
        "SELECT id, name FROM rol WHERE id = %s AND state = 1",
        (id,)
    )
    role = cursor.fetchone()
    if not role:
        conn.close()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    # Proteger roles base del sistema (Admin, Doctor, patient, secretary)
    BASE_ROLES = [1, 2, 3, 4]
    if id in BASE_ROLES:
        conn.close()
        raise HTTPException(
            status_code=403, 
            detail=f"No se puede eliminar el rol base '{role['name']}'"
        )
    
    # Verificar si hay usuarios asignados a este rol
    cursor.execute(
        "SELECT COUNT(*) as count FROM user WHERE id_rol = %s AND state = 1",
        (id,)
    )
    user_count = cursor.fetchone()
    if user_count and user_count['count'] > 0:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el rol porque tiene {user_count['count']} usuario(s) asignado(s)"
        )
    
    # Eliminar el rol (soft delete)
    cursor.execute(
        "UPDATE rol SET state = 0, updated_at = NOW() WHERE id = %s",
        (id,)
    )
    
    # Eliminar permisos asociados (soft delete)
    cursor.execute(
        "UPDATE module_x_rol SET state = 0, updated_at = NOW() WHERE id_rol = %s",
        (id,)
    )
    
    conn.commit()
    conn.close()
    return {"message": "Rol eliminado exitosamente"}