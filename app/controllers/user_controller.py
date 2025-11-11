import mysql.connector
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.user_model import User
from fastapi.encoders import jsonable_encoder
from datetime import datetime, date
import bcrypt


class UserController:
    # ... (create_user, get_user_by_id, get_all_users sin cambios) ...
    def create_user(self, user: User):
        conn = None
        cursor = None
        try:
            print("📥 Datos recibidos del frontend:", user.dict())  # 👈 agrega esto
            conn = get_db_connection()
            cursor = conn.cursor()

            # Hashear la contraseña antes de guardarla
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

            sql = """
                INSERT INTO `user` (
                    user_name, password, full_name, last_name, email, date_birth,
                    address, phone, id_type_document, num_document, id_rol, genero, state
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """

            # Asegura que num_document sea numérico y fecha válida
            try:
                num_doc = int(user.num_document) if user.num_document else None
            except ValueError:
                num_doc = None

            # Control de fecha vacía
            if not user.date_birth:
                user.date_birth = None

            values = (
                user.user_name,
                hashed_password.decode('utf-8'), # Guardar como string
                user.full_name,
                user.last_name,
                user.email,
                user.date_birth,
                user.address,
                user.phone,
                user.id_type_document,
                num_doc,
                user.id_rol,
                getattr(user, 'genero', None),
            )

            print("🧩 Valores para INSERT:", values)  # 👈 agrega esto también

            cursor.execute(sql, values)
            conn.commit()
            new_id = cursor.lastrowid

            # devolver la fila creada
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("SELECT * FROM user WHERE id = %s", (new_id,))
            row = cur2.fetchone()
            cur2.close()
            return jsonable_encoder(row)

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Obtener usuario por ID
    def get_user_by_id(self, user_id: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Unir con type_document para obtener el nombre
            cursor.execute("""
                SELECT u.*, td.name as type_document_name
                FROM user u
                LEFT JOIN type_document td ON u.id_type_document = td.id
                WHERE u.id = %s AND u.state = 1
            """, (user_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Calcular edad a partir de date_birth y agregar campo 'edad' esperado por el frontend
            dob = result.get('date_birth')
            try:
                if dob:
                    # dob puede ser datetime.date o string en formato YYYY-MM-DD
                    if isinstance(dob, str):
                        dob_date = datetime.strptime(dob.split('T')[0], '%Y-%m-%d').date()
                    elif isinstance(dob, datetime):
                        dob_date = dob.date()
                    else:
                        dob_date = dob

                    today = date.today()
                    edad = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                else:
                    edad = None
            except Exception:
                edad = None

            result['edad'] = edad
            return jsonable_encoder(result)

        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=str(err))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Obtener todos los usuarios activos
    def get_all_users(self):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE state = 1")
            result = cursor.fetchall()

            # Añadir campo 'edad' a cada fila según date_birth
            enriched = []
            for row in result:
                dob = row.get('date_birth')
                try:
                    if dob:
                        if isinstance(dob, str):
                            dob_date = datetime.strptime(dob.split('T')[0], '%Y-%m-%d').date()
                        elif isinstance(dob, datetime):
                            dob_date = dob.date()
                        else:
                            dob_date = dob

                        today = date.today()
                        edad = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    else:
                        edad = None
                except Exception:
                    edad = None

                row['edad'] = edad
                enriched.append(row)

            return jsonable_encoder(enriched)

        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=str(err))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    # Actualizar usuario
    def update_user(self, user_id: int, payload: dict):
        conn = None
        cursor = None
        try:
            print("▶ update_user payload:", payload)

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Obtener valores actuales
            cursor.execute("SELECT * FROM user WHERE id = %s AND state = 1", (user_id,))
            current = cursor.fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Construir la consulta dinámicamente
            update_fields = []
            values = []

            for key, value in payload.items():
                if key in ["id", "created_at", "updated_at", "state"]:
                    continue # Ignorar campos no modificables

                if key == "password":
                    if value: # Solo actualizar si se provee una nueva contraseña
                        hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                        update_fields.append("password = %s")
                        values.append(hashed_password.decode('utf-8'))
                else:
                    update_fields.append(f"{key} = %s")
                    values.append(value)
            
            if not update_fields:
                return jsonable_encoder(current) # No hay nada que actualizar

            update_fields.append("updated_at = CURRENT_TIMESTAMP")

            sql = f"UPDATE user SET {', '.join(update_fields)} WHERE id = %s AND state = 1"
            values.append(user_id)

            cursor = conn.cursor()
            cursor.execute(sql, tuple(values))
            conn.commit()

            if cursor.rowcount == 0:
                # Esto puede pasar si el usuario fue eliminado mientras tanto
                raise HTTPException(status_code=404, detail="Usuario no encontrado o no se realizaron cambios.")

            # Devolver la fila actualizada con el nombre del tipo de documento
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("""
                SELECT u.*, td.name as type_document_name
                FROM user u
                LEFT JOIN type_document td ON u.id_type_document = td.id
                WHERE u.id = %s
            """, (user_id,))
            updated = cur2.fetchone()
            cur2.close()
            return jsonable_encoder(updated)

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Eliminar usuario (soft delete)
    def delete_user(self, user_id: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute(
                "UPDATE user SET state = 0, updated_at = %s WHERE id = %s AND state = 1",
                (now, user_id),
            )
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            return {"message": "Usuario eliminado correctamente"}

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
                print("❌ Error MySQL:", err)  # 👈 esto también

            raise HTTPException(status_code=500, detail=str(err))

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
