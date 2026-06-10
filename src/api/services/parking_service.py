import os

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from db.db import get_parking_status_by_plate
from db.user_service_db import fetch_user_by_id


def get_parking_status(user_id: int):
    # Returneaza statusul masinii utilizatorului autentificat
    user_row = fetch_user_by_id(user_id)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Se presupune ca numarul de inmatriculare se afla pe pozitia 5 in row-ul returnat de fetch_user_by_id
    numar_inmatriculare = user_row[5]
    if not numar_inmatriculare:
        return {"status": "invalid"}

    return {"status": get_parking_status_by_plate(numar_inmatriculare)}


def get_user_active_qr(user_id: int):
    # Returneaza fisierul QR pentru utilizatorul dat
    row = fetch_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    qr_path = row[6]
    if not qr_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR not found")

    if not os.path.isabs(qr_path):
        qr_path = os.path.abspath(qr_path)

    if not os.path.exists(qr_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR file not found")

    return FileResponse(qr_path, media_type="image/png", filename=os.path.basename(qr_path))
