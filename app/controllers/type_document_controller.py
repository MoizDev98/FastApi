# app/controllers/type_document_controller.py
from fastapi import HTTPException
from models.type_document import TypeDocument
from config.db_config import get_db_connection
from typing import List, Dict, Any

def create_type_document(doc: TypeDocument) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO type_document (name, abbreviation, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())"
        cursor.execute(sql, (doc.name, doc.abbreviation))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM type_document WHERE id = %s", (new_id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def get_all_type_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM type_document ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def get_type_document_by_id(id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM type_document WHERE id = %s", (id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")
        return row
    finally:
        conn.close()

def update_type_document(id: int, doc: TypeDocument) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # comprobar existencia
        cur.execute("SELECT id FROM type_document WHERE id = %s", (id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")

        cur.execute(
            "UPDATE type_document SET name=%s, abbreviation=%s, updated_at=NOW() WHERE id=%s",
            (doc.name, doc.abbreviation, id)
        )
        conn.commit()
        cur.close()

        # devolver fila actualizada
        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM type_document WHERE id = %s", (id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def delete_type_document(id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM type_document WHERE id = %s", (id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")

        cur.execute("DELETE FROM type_document WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        return {"message": "Tipo de documento eliminado correctamente"}
    finally:
        conn.close()
