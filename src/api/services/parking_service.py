import os
from datetime import datetime

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from db import (
    fetch_active_subscription_plan_by_plate,
    get_parking_fee,
    get_parking_status_by_plate,
    pay_parking,
)
from src.db.users import fetch_user_by_id


def get_parking_status(user_id: int):
    # Returneaza statusul masinii utilizatorului autentificat
    user_row = fetch_user_by_id(user_id)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Se presupune ca numarul de inmatriculare se afla pe pozitia 5 in row-ul returnat de fetch_user_by_id
    numar_inmatriculare = user_row[5]
    if not numar_inmatriculare:
        return {"status": "invalid", "grace_seconds_remaining": None}

    parking_status = get_parking_status_by_plate(numar_inmatriculare)
    # Daca parcarea este platita, calculam timpul ramas din perioada de gratie de 5 minute
    grace_seconds_remaining = None
    if parking_status == "paid":
        try:
            cursor_data = get_parking_fee(numar_inmatriculare=numar_inmatriculare)
            if cursor_data:
                remaining = max(0, int(5 * 60 - cursor_data["billable_minutes"] * 60))
                grace_seconds_remaining = remaining
        except Exception:
            grace_seconds_remaining = None

    return {
        "status": parking_status,
        "grace_seconds_remaining": grace_seconds_remaining,
    }


def _get_user_plate(user_id: int) -> str:
    user_row = fetch_user_by_id(user_id)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    numar_inmatriculare = user_row[5]
    if not numar_inmatriculare:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niciun utilizator nu a fost gasit cu acest numar de inmatriculare.",
        )
    return numar_inmatriculare


def get_user_parking_fee(user_id: int):
    numar_inmatriculare = _get_user_plate(user_id)
    if fetch_active_subscription_plan_by_plate(numar_inmatriculare):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Abonamentul este activ. Nu este necesara plata parcarii.",
        )

    parking_status = get_parking_status_by_plate(numar_inmatriculare)
    if parking_status == "invalid":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Niciun vehicul asociat acestui utilizator nu a fost gasit.",
        )
    if parking_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Parcarea este deja platita.",
        )

    try:
        fee = get_parking_fee(numar_inmatriculare=numar_inmatriculare)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nu s-a putut calcula taxa de parcare pentru acest vehicul.",
        )

    return {**fee, "currency": "RON"}


def pay_user_parking(
    user_id: int,
    parking_code: str,
    expected_amount: float,
):
    fee = get_user_parking_fee(user_id)
    if fee["parking_code"] != parking_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Codul de parcare a fost modificat. Reincarcati pagina pentru a vedea noile detalii de plata.",
        )
    if round(fee["amount"], 2) != round(expected_amount, 2):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Taxa de parcare a fost modificata. Reîncarcați pagina pentru a vedea noile detalii de plata.",
        )

    payment_result = pay_parking(parking_code)
    if payment_result == "already_paid":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Parcarea este deja achitata.",
        )
    if payment_result != "success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plata pentru parcare nu a putut fi înregistrata. Va rugam sa încercați din nou mai tarziu.",
        )

    return {
        "paid": True,
        "parking_code": parking_code,
        "amount": fee["amount"],
        "currency": "RON",
        "message": "Plata pentru parcare a fost înregistrata cu succes.",
    }


def get_user_active_qr(user_id: int):
    # Returneaza fisierul QR pentru utilizatorul dat
    row = fetch_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizatorul nu a fost gasit.")

    numar_inmatriculare = row[5]
    if not numar_inmatriculare:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niciun numar de inmatriculare asociat utilizatorului.")

    parking_status = get_parking_status_by_plate(numar_inmatriculare)
    if parking_status == "invalid":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Masina nu se afla in parcare.")

    qr_path = row[6]
    if not qr_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR-ul nu a fost gasit.")

    if not os.path.isabs(qr_path):
        qr_path = os.path.abspath(qr_path)

    if not os.path.exists(qr_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fișierul QR nu a fost gasit.")

    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(
        qr_path,
        media_type="image/png",
        filename=os.path.basename(qr_path),
        headers=headers,
    )
