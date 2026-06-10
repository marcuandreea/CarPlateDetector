import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError

SECRET_KEY = os.getenv("PARKING_API_SECRET", "change-me-in-production")
ALGORITHM = os.getenv("PARKING_API_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("PARKING_API_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    # Creeaza un token JWT cu un user_id si o data de expirare
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    # Decodeaza tokenul JWT si returneaza payload-ul
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def is_token_valid(token: str) -> bool:
    # Verifica daca tokenul JWT este valid
    try:
        decode_access_token(token)
        return True
    except JWTError:
        return False
