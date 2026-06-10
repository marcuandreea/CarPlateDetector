from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user_id
from services.parking_service import get_parking_status, get_user_active_qr

router = APIRouter(tags=["parking"])

# Endpoint pentru obtinerea statusului masinii utilizatorului curent
@router.get("/parking-status")
def parking_status(current_user_id: int = Depends(get_current_user_id)):
    return get_parking_status(current_user_id)

# Endpoint pentru obtinerea QR-ului activ al utilizatorului curent
@router.get("/active-qr")
def active_qr(current_user_id: int = Depends(get_current_user_id)):
    return get_user_active_qr(current_user_id)
