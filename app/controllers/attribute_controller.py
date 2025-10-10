from fastapi import HTTPException
from models.attribute_model import Attribute
from database import get_db_connection
from typing import List, Dict, Any

def create_attribute(attr: Attribute) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = "INSERT INTO attribute (name, description, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())"
        cur.execute(sql, (attr.name, attr.description))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM attribute WHERE id = %s", (new_id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def get_all_attributes() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM attribute ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def get_attribute_by_id(id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM attribute WHERE id = %s", (id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Atributo no encontrado")
        return row
    finally:
        conn.close()

def update_attribute(id: int, attr: Attribute) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM attribute WHERE id = %s", (id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="Atributo no encontrado")

        cur.execute(
            "UPDATE attribute SET name=%s, description=%s, updated_at=NOW() WHERE id=%s",
            (attr.name, attr.description, id)
        )
        conn.commit()
        cur.close()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT * FROM attribute WHERE id = %s", (id,))
        row = cur2.fetchone()
        cur2.close()
        return row
    finally:
        conn.close()

def delete_attribute(id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM attribute WHERE id = %s", (id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="Atributo no encontrado")

        cur.execute("DELETE FROM attribute WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        return {"message": "Atributo eliminado correctamente"}
    finally:
        conn.close()
