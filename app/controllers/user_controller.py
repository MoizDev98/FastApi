import mysql.connector
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.user_model import User
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from datetime import date


class UserController:
    # Crear usuario
    def create_user(self, user: User):
        conn = None
        cursor = None
        try:
            print("📥 Datos recibidos del frontend:", user.dict())  # 👈 agrega esto
            conn = get_db_connection()
            cursor = conn.cursor()

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
                user.password,
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

            return {"message": "Usuario creado correctamente", "id": new_id}

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
            cursor.execute("SELECT * FROM user WHERE id = %s AND state = 1", (user_id,))
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
    def update_user(self, user_id: int, user: User):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now = datetime.now()

            sql = """
                UPDATE user
                SET user_name=%s, password=%s, full_name=%s, last_name=%s, email=%s,
                    date_birth=%s, address=%s, phone=%s, id_type_document=%s,
                    num_document=%s, id_rol=%s, genero=%s, updated_at=%s
                WHERE id=%s AND state = 1
            """
            values = (
                user.user_name,
                user.password,
                user.full_name,
                user.last_name,
                user.email,
                user.date_birth,
                user.address,
                user.phone,
                user.id_type_document,
                user.num_document,
                user.id_rol,
                getattr(user, 'genero', None),
                now,
                user_id,
            )

            cursor.execute(sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            return {"message": "Usuario actualizado correctamente"}

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
