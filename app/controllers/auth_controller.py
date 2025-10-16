from fastapi import HTTPException
from config.db_config import get_db_connection
from models.login_request import LoginRequest
import mysql.connector


def login(request: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_name = %s and password = %s",
                       (request.username, request.password))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code = 404, detail = "Invalid username or password")

        return {
            "message": "Login successful",
            "user_id": result[0],
            "name": result[3],
            "lastName": result[4],
        }

    except mysql.connector.Error as err:
        print(err)
        conn.rollback()
    finally:
        conn.close()
