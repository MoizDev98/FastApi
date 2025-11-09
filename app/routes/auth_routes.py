from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from config.db_config import get_db_connection
from config.security import create_access_token
from config.security import get_current_user

# Opcional: activar bcrypt cuando migres passwords
# import bcrypt

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    conn = get_db_connection()
    # DEBUG LOGS (elimina luego en producción)
    print("[AUTH] Intento login username/email=", req.username)
    cur = conn.cursor(dictionary=True)
    # Permitir login por user_name o email
    cur.execute(
        "SELECT * FROM user WHERE (user_name=%s OR email=%s) AND state=1",
        (req.username, req.username),
    )
    user = cur.fetchone()
    print("[AUTH] Usuario encontrado?", bool(user))
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Soporte dual: primero intenta bcrypt, si falla, compara en texto plano
    stored_pwd = user.get("password") or ""
    incoming_pwd = req.password or ""
    print("[AUTH] Longitudes -> stored:", len(stored_pwd), " incoming:", len(incoming_pwd))
    # Evitar imprimir la contraseña completa por seguridad
    is_valid = False
    try:
        import importlib  # evitar error de import estático en linters
        bcrypt = importlib.import_module("bcrypt")
        try:
            # bcrypt espera bytes
            if stored_pwd and bcrypt.checkpw(incoming_pwd.encode("utf-8"), stored_pwd.encode("utf-8")):
                is_valid = True
                print("[AUTH] Coincidencia bcrypt OK")
        except ValueError:
            # hash inválido -> ignorar y seguir con comparación plana
            is_valid = False
    except Exception:
        # bcrypt no disponible o error de import -> continuar con comparación plana
        pass

    if not is_valid:
        # Fallback a texto plano (solo para compatibilidad temporal)
        if stored_pwd == incoming_pwd:
            is_valid = True
            print("[AUTH] Coincidencia texto plano OK")

    if not is_valid:
        print("[AUTH] Falló validación de contraseña")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({
        "sub": str(user["id"]),
        "user_name": user.get("user_name"),
        "id_rol": user.get("id_rol"),
    })
    print("[AUTH] Login exitoso para user id=", user.get("id"))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    # No exponer password
    current_user = dict(current_user)
    current_user.pop("password", None)
    return current_user
