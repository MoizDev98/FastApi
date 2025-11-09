from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from config.db_config import get_db_connection

# NOTA: mueve este SECRET_KEY a variables de entorno en producción
SECRET_KEY = "CHANGE_ME_WITH_A_LONG_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _get_user_by_id(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM user WHERE id=%s AND state=1", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        user_id = int(sub) if sub is not None else None
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = _get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user
