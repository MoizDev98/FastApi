from fastapi import APIRouter, HTTPException, Request
from config.db_config import get_db_connection

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/{patient_id}")
def get_patient(patient_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM user WHERE id = %s AND state = 1", (patient_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return row
    finally:
        conn.close()


@router.patch("/{patient_id}")
async def patch_patient(patient_id: int, request: Request):
    """Actualiza campos parciales del paciente; acepta JSON con solo los campos a modificar."""
    payload = await request.json()
    if not isinstance(payload, dict) or len(payload) == 0:
        raise HTTPException(status_code=400, detail="Payload vacío")

    # Mapeo de campos permitidos -> columnas
    allowed = {
        "user_name": "user_name",
        "password": "password",
        "full_name": "full_name",
        "last_name": "last_name",
        "email": "email",
        "date_birth": "date_birth",
        "address": "address",
        "phone": "phone",
        "id_type_document": "id_type_document",
        "num_document": "num_document",
        "id_rol": "id_rol",
        "genero": "genero",
    }

    set_clauses = []
    values = []
    for k, v in payload.items():
        col = allowed.get(k)
        if not col:
            continue
        set_clauses.append(f"{col} = %s")
        values.append(v)

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No hay campos válidos para actualizar")

    set_sql = ", ".join(set_clauses) + ", updated_at = NOW()"
    values.append(patient_id)

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET {set_sql} WHERE id = %s AND state = 1", tuple(values))
        conn.commit()
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM user WHERE id = %s", (patient_id,))
        row = cur2.fetchone()
        cur2.close()
        if not row:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return row
    finally:
        conn.close()
