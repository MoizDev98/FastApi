import mysql.connector
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.user_model import User
from fastapi.encoders import jsonable_encoder
from datetime import datetime

class UserController:
     #create user in the table Users   
    def create_user(self, user: User):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre,apellido,cedula,edad,usuario,contrasena) VALUES (%s, %s, %s, %s, %s ,%s)", (user.nombre, user.apellido, user.cedula, user.edad, user.usuario, user.contrasena))
            conn.commit()
            conn.close()
            return {"resultado": "Usuario creado"}
        except mysql.connector.Error as err:
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
    
    #get user by id
    def get_user(self, user_id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            
            content={
                    'id':int(result[0]),
                    'nombre':result[1],
                    'apellido':result[2],
                    'cedula':result[3],
                    'edad':int(result[4]),
                    'usuario':result[5],
                    'contrasena':result[6]
            }
            payload.append(content)
            
            json_data = jsonable_encoder(content)            
            if result:
               return  json_data
            else:
                ##Esto interrumpe la ejecución y responde al cliente con un código 404
                ## comunica al cliente de la API qué pasó (error HTTP).
                ##código 404,comportamiento correcto según las reglas HTTP
                raise HTTPException(status_code=404, detail="User not found")  
                
        except mysql.connector.Error as err:
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            ##Maneja el estado de la transacción en la base de datos.Si un INSERT, UPDATE o DELETE falla dentro de una transacción, rollback() revierte esos cambios.
            conn.rollback()
        finally:
            conn.close()
    
    #get all users   
    def get_users(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id':data[0],
                    'nombre':data[1],
                    'cedula':data[2],
                    'edad':data[3],
                    'usuario':data[4],
                    'contrasena':data[5]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="User not found")  
                
        except mysql.connector.Error as err:
            conn.rollback()
        finally:
            conn.close()
    
    #update user by id
    def update_user(user_id: int, user: User):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute("""
            UPDATE user
            SET user_name=%s, password=%s, first_name=%s, middle_name=%s, email=%s,
                date_birthday=%s, address=%s, phone=%s, specialty=%s,
                id_type_document=%s, id_rol=%s, updated_at=%s
            WHERE id=%s
        """, (
            user.user_name, user.password, user.first_name, user.middle_name, user.email,
            user.date_birthday, user.address, user.phone, user.specialty,
            user.id_type_document, user.id_rol, now, user_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User updated successfully"}
    
    #delete user by id
    def delete_user(user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User deleted successfully"}
    
       

