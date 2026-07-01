from fastapi import HTTPException, status

from auth.jwt import create_access_token
from auth.password import hash_password, verify_password
from db.user_service_db import (
    fetch_user_by_email,
    fetch_user_by_id,
    fetch_user_by_plate,
    insert_user,
    update_user,
)


def _build_profile_payload(row):
    # Construieste payload-ul pentru profilul userului pe baza datelor din baza de date
    return {
        "id": row[0],
        "nume": row[1],
        "prenume": row[2],
        "email": row[3],
        "numar_inmatriculare": row[5],
        "qr_path": row[6],
    }


def register_user(payload):
    # Inregistreaza un nou user, verificand unicitatea email-ului si numarului de inmatriculare
    if fetch_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email existent")

    if fetch_user_by_plate(payload.numar_inmatriculare):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numarul de inmatriculare existent")

    # Cripteaza parola folosind functia de criptare
    password_hash = hash_password(payload.password)
    user_id = insert_user(
        payload.nume,
        payload.prenume,
        payload.email,
        password_hash,
        payload.numar_inmatriculare,
    )
    return {"id": user_id}


def login_user(payload):
    # Autentifica un user, returnand un token JWT
    user_row = fetch_user_by_email(payload.email)
    if not user_row or not verify_password(payload.password, user_row[4]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user_row[0]))
    profile = _build_profile_payload(user_row)
    return {"access_token": token, "token_type": "bearer", "user": profile}


def get_profile(user_id: int):
    # Returneaza profilul unui user dupa id
    row = fetch_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _build_profile_payload(row)


def update_profile(user_id: int, payload):
    # Actualizeaza profilul unui user
    current_row = fetch_user_by_id(user_id)
    if not current_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    values = {}

    # Verifica fiecare camp din payload si il adauga in dict-ul values
    if payload.nume is not None:
        values["nume"] = payload.nume
    if payload.prenume is not None:
        values["prenume"] = payload.prenume
    if payload.email is not None:
        existing = fetch_user_by_email(payload.email)
        if existing and existing[0] != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        values["email"] = payload.email
    if payload.numar_inmatriculare is not None:
        existing = fetch_user_by_plate(payload.numar_inmatriculare)
        if existing and existing[0] != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numar inmatriculare already exists")
        values["numar_inmatriculare"] = payload.numar_inmatriculare
    if payload.password is not None:
        values["password_hash"] = hash_password(payload.password)

    update_user(user_id, values)
    return get_profile(user_id)
