# app/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv

load_dotenv()

# --------- PASSWORD HASH (Argon2) ---------

ph = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,  # 64 MB
    parallelism=2,
)

MAX_PW_LEN = 128  # por seguridad, recortamos passwords absurdamente largas

def hash_password(password: str) -> str:
    """
    Hashea la contraseña usando Argon2.
    """
    if not isinstance(password, str):
        password = str(password)
    password = password[:MAX_PW_LEN]
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica la contraseña usando Argon2.
    """
    try:
        plain = (plain or "")[:MAX_PW_LEN]
        ph.verify(hashed, plain)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False
    except Exception:
        return False

# --------- JWT ---------

SECRET_KEY = os.getenv("SECRET_KEY", "CAMBIA_ESTE_SECRETO_LARGO_Y_ALEATORIO")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """
    Crea un JWT con 'sub' = subject (normalmente el email).
    """
    expire_delta = timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": subject,
        "exp": datetime.now(tz=timezone.utc) + expire_delta,
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    """
    Decodifica un JWT y retorna el 'sub' (email).
    Lanza ValueError con mensaje legible si falla.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Token sin 'sub'.")
        return sub
    except ExpiredSignatureError:
        raise ValueError("Token expirado.")
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}")

# Alias para mantener compatibilidad si en algún lado importas decode_access_token
def decode_access_token(token: str) -> str:
    return decode_token(token)
