# controllers/appointment_controller.py
from database import get_db_connection
from typing import List, Dict, Any, Optional
from datetime import datetime

def create_appointment(data) -> Dict[str, Any]:
    """
    data: objeto Pydantic AppointmentCreate o similar (tiene id_user, appointment_date, id_state)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO appointment (id_user, appointment_date, id_state, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """
        values = (
            data.id_user,
            data.appointment_date,
            data.id_state
        )
        cursor.execute(sql, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        # devolver la fila recién creada como dict
        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM appointment WHERE id_appointment = %s", (new_id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def get_all_appointments() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM appointment ORDER BY appointment_date DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def get_appointment_by_id(appointment_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM appointment WHERE id_appointment = %s", (appointment_id,))
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        conn.close()

def update_appointment(appointment_id: int, data) -> Optional[Dict[str, Any]]:
    """
    data: AppointmentUpdate (puede ser parcial)
    Devuelve la fila actualizada como dict o None si no hubo campos para actualizar.
    """
    # construir SET dinámico
    set_clauses = []
    values = []

    field_map = {
        "id_user": "id_user",
        "appointment_date": "appointment_date",
        "id_state": "id_state",
    }

    for schema_field, db_col in field_map.items():
        val = getattr(data, schema_field, None)
        if val is not None:
            set_clauses.append(f"{db_col} = %s")
            values.append(val)

    if not set_clauses:
        return None

    set_sql = ", ".join(set_clauses) + ", updated_at = NOW()"
    values.append(appointment_id)

    sql = f"UPDATE appointment SET {set_sql} WHERE id_appointment = %s"

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(values))
        conn.commit()
        cur.close()

        # devolver fila actualizada
        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM appointment WHERE id_appointment = %s", (appointment_id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def delete_appointment(appointment_id: int) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM appointment WHERE id_appointment = %s", (appointment_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()
