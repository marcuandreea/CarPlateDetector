from fastapi import Header, HTTPException, status

from auth.jwt import decode_access_token

def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    # Dependency pentru a extrage user_id din tokenul JWT
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Lipsă sau invalid token de autentificare")

    # Extrage tokenul din header si extrage user_id folosind functia de decodare
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Lipsă subiect")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid sau expirat")
