# controllers/appointment_controller.py
from config.db_config import get_db_connection
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.email_service import EmailService
from fastapi import HTTPException

email_service = EmailService()

def create_appointment(data, created_by_id: int = None) -> Dict[str, Any]:
    """Crea una cita. Soporta id_user_doctor opcional."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO appointment (id_user, id_user_doctor, appointment_date, id_state, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        values = (
            data.id_user,
            getattr(data, "id_user_doctor", None),
            data.appointment_date,
            data.id_state
        )
        cursor.execute(sql, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM appointment WHERE id_appointment = %s", (new_id,))
        row = cur2.fetchone()
        cur2.close()
        
        # Enviar email de notificación al paciente
        try:
            cur3 = conn.cursor(dictionary=True)
            cur3.execute("""
                SELECT u.email, u.full_name, d.full_name as doctor_name
                FROM user u
                LEFT JOIN user d ON d.id_user = %s
                WHERE u.id_user = %s
            """, (getattr(data, "id_user_doctor", None), data.id_user))
            user_data = cur3.fetchone()
            cur3.close()
            
            if user_data:
                email_service.send_new_appointment(
                    to_email=user_data['email'],
                    patient_name=user_data['full_name'],
                    appointment_date=data.appointment_date.strftime("%d/%m/%Y %H:%M"),
                    doctor_name=user_data.get('doctor_name', 'Por asignar')
                )
        except Exception as e:
            print(f"Error enviando email: {e}")
            # No fallar si el email no se envía
        
        return row
    finally:
        conn.close()

def get_all_appointments() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT a.id_appointment, a.id_user, a.id_user_doctor, a.appointment_date, 
                   a.id_state, a.created_at, a.updated_at,
                   CONCAT(COALESCE(u.full_name, ''), ' ', COALESCE(u.last_name, '')) AS patient_name
            FROM appointment a
            LEFT JOIN user u ON a.id_user = u.id
            ORDER BY a.appointment_date DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        # Limpiar espacios en blanco del patient_name
        for row in rows:
            if row.get('patient_name'):
                row['patient_name'] = row['patient_name'].strip()
                if not row['patient_name']:
                    row['patient_name'] = None
        
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
        "id_user_doctor": "id_user_doctor",
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

def get_filtered_appointments(
    doctor_id: Optional[int] = None,
    state: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 200,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Devuelve citas filtradas con soporte de paginación básica, incluyendo el nombre del paciente."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        where = []
        values: List[Any] = []

        if doctor_id is not None:
            where.append("a.id_user_doctor = %s")
            values.append(doctor_id)
        if state is not None:
            where.append("a.id_state = %s")
            values.append(state)
        if date_from is not None:
            where.append("a.appointment_date >= %s")
            values.append(date_from)
        if date_to is not None:
            where.append("a.appointment_date <= %s")
            values.append(date_to)

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT a.id_appointment, a.id_user, a.id_user_doctor, a.appointment_date, 
                   a.id_state, a.created_at, a.updated_at,
                   CONCAT(COALESCE(u.full_name, ''), ' ', COALESCE(u.last_name, '')) AS patient_name
            FROM appointment a
            LEFT JOIN user u ON a.id_user = u.id
            {where_sql}
            ORDER BY a.appointment_date DESC
            LIMIT %s OFFSET %s
        """
        values.extend([limit, offset])
        cur.execute(sql, tuple(values))
        rows = cur.fetchall()
        
        # Limpiar espacios en blanco del patient_name
        for row in rows:
            if row.get('patient_name'):
                row['patient_name'] = row['patient_name'].strip()
                if not row['patient_name']:
                    row['patient_name'] = None
        
        cur.close()
        return rows
    finally:
        conn.close()


def update_appointment_status(appointment_id: int, new_state_id: int, changed_by_id: int):
    """Actualiza el estado de una cita y envía notificación por email al paciente"""
    conn = get_db_connection()
    try:
        # Obtener información de la cita
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT a.*, u.email as patient_email, u.full_name as patient_name,
                   s.name as state_name, d.full_name as doctor_name
            FROM appointment a
            JOIN user u ON a.id_user = u.id_user
            LEFT JOIN state_appointment s ON s.id_state_appointment = %s
            LEFT JOIN user d ON a.id_user_doctor = d.id_user
            WHERE a.id_appointment = %s
        """
        cur.execute(query, (new_state_id, appointment_id))
        appointment_data = cur.fetchone()
        
        if not appointment_data:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Actualizar el estado
        cur.execute(
            "UPDATE appointment SET id_state = %s, updated_at = NOW() WHERE id_appointment = %s",
            (new_state_id, appointment_id)
        )
        conn.commit()
        
        # Enviar email al paciente
        try:
            email_service.send_appointment_status_changed(
                to_email=appointment_data['patient_email'],
                patient_name=appointment_data['patient_name'],
                appointment_date=appointment_data['appointment_date'].strftime("%d/%m/%Y %H:%M"),
                new_status=appointment_data['state_name'] or 'Actualizado',
                changed_by=appointment_data['doctor_name'] or 'Personal médico'
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        cur.close()
        return {"message": "Estado actualizado correctamente", "appointment_id": appointment_id}
    finally:
        conn.close()
