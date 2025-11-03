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
    def update_user(self, user_id: int, payload: dict):
        """Actualizar usuario: acepta un dict parcial con los campos a modificar.
        Si un campo no está presente, conserva el valor actual en la DB.
        """
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

            # Para cada campo, si está presente en payload usar ese valor, sino mantener el actual
            def use(key):
                return payload[key] if key in payload else current.get(key)

            # normalizaciones
            num_document = None
            if 'num_document' in payload and payload.get('num_document') not in (None, ''):
                try:
                    num_document = int(payload.get('num_document'))
                except Exception:
                    num_document = None
            else:
                num_document = current.get('num_document')

            date_birth = payload.get('date_birth') if 'date_birth' in payload else current.get('date_birth')

            sql = """
                UPDATE user
                SET user_name=%s, password=%s, full_name=%s, last_name=%s, email=%s,
                    date_birth=%s, address=%s, phone=%s, id_type_document=%s,
                    num_document=%s, id_rol=%s, genero=%s, updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND state = 1
            """

            values = (
                use('user_name'),
                use('password'),
                use('full_name'),
                use('last_name'),
                use('email'),
                date_birth,
                use('address'),
                use('phone'),
                use('id_type_document'),
                num_document,
                use('id_rol'),
                payload.get('genero') if 'genero' in payload else current.get('genero'),
                user_id,
            )

            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Devolver la fila actualizada
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("SELECT * FROM user WHERE id = %s", (user_id,))
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
