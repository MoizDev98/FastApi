from fastapi import HTTPException
from config.db_config import get_db_connection
from models.analysis import Analysis
from services.email_service import EmailService

email_service = EmailService()

# NOTA: La tabla real usa id_analysis como PK y NO tiene name/description.
# Para evitar romper el frontend, devolvemos "id" como alias de id_analysis.

# Crear un nuevo análisis
def create_analysis(analysis: Analysis):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO analysis (id_user, id_disease, id_user_doctor, date, id_state_analysis, result_ia, observation_doctor, url_image, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        # Estado inicial: si no llega, por defecto Pending (1)
        _state_init = (
            getattr(analysis, 'id_state_analysis', None)
            if getattr(analysis, 'id_state_analysis', None) is not None
            else getattr(analysis, 'id_state', None)
        )
        if _state_init is None:
            _state_init = 1

        values = (
            getattr(analysis, 'id_user', None),
            getattr(analysis, 'id_disease', None),
            getattr(analysis, 'id_user_doctor', None),
            getattr(analysis, 'date', None),
            _state_init,
            getattr(analysis, 'result_ia', None),
            getattr(analysis, 'observation_doctor', None),
            getattr(analysis, 'url_image', None),
        )
        cur.execute(query, values)
        conn.commit()
        new_id = cur.lastrowid
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute(
            """
            SELECT 
              id_analysis AS id,
              id_analysis,
              id_user,
              id_disease,
              id_user_doctor,
              date,
              result_ia,
              COALESCE(id_state_analysis, 1) AS id_state,
              observation_doctor,
              url_image,
              created_at,
              updated_at,
              state
            FROM analysis WHERE id_analysis = %s
            """,
            (new_id,)
        )
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

# Obtener todos los análisis
def get_all_analysis():
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT 
              id_analysis AS id,
              id_analysis,
              id_user,
              id_disease,
              id_user_doctor,
              date,
              result_ia,
              COALESCE(id_state_analysis, 1) AS id_state,
              observation_doctor,
              url_image,
              created_at,
              updated_at,
              state
            FROM analysis
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

# Obtener todos los análisis de un paciente por id_user
from fastapi import HTTPException
from app.database import get_db_connection

# ...

def get_analysis_by_user(user_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT
              id_analysis AS id,
              id_analysis,
              id_user,
              id_disease,
              id_user_doctor,
              date,
              status,
              result_ia,
              confidence,
              observation_doctor,
              url_image,
              created_at,
              updated_at,
              state,
              id_state_analysis
            FROM analysis
            WHERE id_user = %s AND state = 1
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Obtener un análisis por ID
def get_analysis_by_id(analysis_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT 
              id_analysis AS id,
              id_analysis,
              id_user,
              id_disease,
              id_user_doctor,
              date,
              result_ia,
              COALESCE(id_state_analysis, 1) AS id_state,
              observation_doctor,
              url_image,
              created_at,
              updated_at,
              state
            FROM analysis WHERE id_analysis = %s
            """,
            (analysis_id,)
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return row
    finally:
        conn.close()

# Actualizar un análisis
def update_analysis(analysis_id: int, analysis: Analysis):
    conn = get_db_connection()
    try:
        # Construir update dinámico solo con campos provistos
        set_cols = []
        values = []
        mapping = {
            'id_user': getattr(analysis, 'id_user', None),
            'id_disease': getattr(analysis, 'id_disease', None),
            'id_user_doctor': getattr(analysis, 'id_user_doctor', None),
            'date': getattr(analysis, 'date', None),
            'result_ia': getattr(analysis, 'result_ia', None),
            'id_state_analysis': (
                getattr(analysis, 'id_state_analysis', None)
                if getattr(analysis, 'id_state_analysis', None) is not None
                else getattr(analysis, 'id_state', None)
            ),
            'observation_doctor': getattr(analysis, 'observation_doctor', None),
            'url_image': getattr(analysis, 'url_image', None),
        }
        for col, val in mapping.items():
            if val is not None:
                set_cols.append(f"{col} = %s")
                values.append(val)
        if not set_cols:
            # nada que actualizar: devolver actual
            cur2 = conn.cursor(dictionary=True)
            cur2.execute(
                "SELECT id_analysis AS id, id_analysis, id_user, id_disease, id_user_doctor, date, result_ia, COALESCE(id_state_analysis, 1) AS id_state, observation_doctor, url_image, created_at, updated_at, state FROM analysis WHERE id_analysis = %s",
                (analysis_id,)
            )
            row = cur2.fetchone()
            cur2.close()
            if not row:
                raise HTTPException(status_code=404, detail="Análisis no encontrado")
            return row

        set_sql = ", ".join(set_cols) + ", updated_at = NOW()"
        values.append(analysis_id)
        sql = f"UPDATE analysis SET {set_sql} WHERE id_analysis = %s"
        cur = conn.cursor()
        cur.execute(sql, tuple(values))
        conn.commit()
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute(
            "SELECT id_analysis AS id, id_analysis, id_user, id_disease, id_user_doctor, date, result_ia, COALESCE(id_state_analysis, 1) AS id_state, observation_doctor, url_image, created_at, updated_at, state FROM analysis WHERE id_analysis = %s",
            (analysis_id,)
        )
        row = cur2.fetchone()
        cur2.close()
        if not row:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return row
    finally:
        conn.close()

# Eliminar un análisis
def delete_analysis(analysis_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM analysis WHERE id_analysis = %s", (analysis_id,))
        conn.commit()
        cur.close()
        return {"message": "Analysis deleted successfully"}
    finally:
        conn.close()


def update_analysis_status(analysis_id: int, new_state_id: int, changed_by_id: int):
    """Actualiza el estado de un análisis y envía notificación por email al paciente"""
    conn = get_db_connection()
    try:
        # Obtener información del análisis y el paciente
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT a.*, u.email as patient_email, u.full_name as patient_name,
                   s.name as state_name, d.full_name as doctor_name
            FROM analysis a
            JOIN user u ON a.id_user = u.id_user
            LEFT JOIN state_analysis s ON s.id_state_analysis = %s
            LEFT JOIN user d ON a.id_user_doctor = d.id_user
            WHERE a.id_analysis = %s
        """
        cur.execute(query, (new_state_id, analysis_id))
        analysis_data = cur.fetchone()
        
        if not analysis_data:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        
        # Actualizar el estado
        cur.execute(
            "UPDATE analysis SET id_state_analysis = %s, updated_at = NOW() WHERE id_analysis = %s",
            (new_state_id, analysis_id)
        )
        conn.commit()
        
        # Enviar email al paciente
        try:
            email_service.send_analysis_status_changed(
                to_email=analysis_data['patient_email'],
                patient_name=analysis_data['patient_name'],
                analysis_id=analysis_id,
                new_status=analysis_data['state_name'] or 'Actualizado',
                changed_by=analysis_data['doctor_name'] or 'Doctor'
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
            # No fallar si el email no se envía
        
        cur.close()
        return {"message": "Estado actualizado correctamente", "analysis_id": analysis_id}
    finally:
        conn.close()


def upload_analysis_image(user_id: int, image_path: str):
    """Registra la subida de una imagen de análisis y envía confirmación por email"""
    conn = get_db_connection()
    try:
        # Obtener email del usuario
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT email, full_name FROM user WHERE id_user = %s", (user_id,))
        user_data = cur.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Aquí podrías crear un registro del análisis o actualizar uno existente
        # Por ahora solo enviaremos el email de confirmación
        
        try:
            email_service.send_analysis_uploaded_confirmation(
                to_email=user_data['email'],
                patient_name=user_data['full_name'],
                upload_date=datetime.now().strftime("%d/%m/%Y %H:%M")
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        cur.close()
        return {"message": "Imagen subida correctamente", "image_path": image_path}
    finally:
        conn.close()


def update_analysis_observation(analysis_id: int, observation: str):
    """Actualiza únicamente la observación del doctor para un análisis existente."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Al guardar observación, pasar a Reviewed (2)
        cur.execute(
            "UPDATE analysis SET observation_doctor = %s, id_state_analysis = %s, updated_at = NOW() WHERE id_analysis = %s",
            (observation, 2, analysis_id),
        )
        conn.commit()
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute(
            "SELECT id_analysis AS id, id_analysis, id_user, id_disease, id_user_doctor, date, result_ia, COALESCE(id_state_analysis, 1) AS id_state, observation_doctor, url_image, created_at, updated_at, state FROM analysis WHERE id_analysis = %s",
            (analysis_id,)
        )
        row = cur2.fetchone()
        cur2.close()
        if not row:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return row
    finally:
        conn.close()
from datetime import datetime

