from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user_id
from models.parking import (
    ParkingFeeResponse,
    ParkingPaymentRequest,
    ParkingPaymentResponse,
)
from services.parking_service import (
    get_parking_status,
    get_user_active_qr,
    get_user_parking_fee,
    pay_user_parking,
)

router = APIRouter(tags=["parking"])

# Endpoint pentru obtinerea statusului masinii utilizatorului curent
@router.get("/parking-status")
def parking_status(current_user_id: int = Depends(get_current_user_id)):
    return get_parking_status(current_user_id)


@router.get("/parking-fee", response_model=ParkingFeeResponse)
def parking_fee(current_user_id: int = Depends(get_current_user_id)):
    return get_user_parking_fee(current_user_id)


@router.post("/pay-parking", response_model=ParkingPaymentResponse)
def pay_parking(
    payload: ParkingPaymentRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    return pay_user_parking(
        current_user_id,
        payload.parking_code,
        payload.expected_amount,
    )


# Endpoint pentru obtinerea QR-ului activ al utilizatorului curent
@router.get("/active-qr")
def active_qr(current_user_id: int = Depends(get_current_user_id)):
    return get_user_active_qr(current_user_id)
