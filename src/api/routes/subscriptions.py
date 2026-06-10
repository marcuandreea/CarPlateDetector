from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user_id
from db.db import activate_subscription, fetch_subscription_plans, fetch_active_subscription_by_user_id
from models.subscription import SubscriptionActivateRequest

router = APIRouter(tags=["subscriptions"])

# Endpoint pentru listarea tipurilor de abonamente disponibile
@router.get("/subscription-plans")
def list_subscription_plans():
    return [
        {
            "id": plan_id,
            "nume": nume,
            "price": float(price),
            "duration": duration,
        }
        for plan_id, nume, price, duration in fetch_subscription_plans()
    ]

# Endpoint pentru obtinerea abonamentului activ
@router.get("/subscriptions/active")
def get_active_subscription(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
):
    sub = fetch_active_subscription_by_user_id(current_user_id)
    if not sub:
        return None
    return {
        "id": sub[0],
        "user_id": sub[1],
        "start_date": sub[2],
        "end_date": sub[3],
        "plan_id": sub[4],
        "active": sub[5],
        "plan_nume": sub[6],
        "plan_price": float(sub[7]),
        "plan_duration": sub[8]
    }

# Endpoint pentru activarea unui abonament pentru utilizatorul curent
@router.post("/subscriptions/activate")
def activate_subscription_for_user(
    payload: SubscriptionActivateRequest,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
):
    user_subscription_id = activate_subscription(current_user_id, payload.subscription_id)
    return {"subscription_id": user_subscription_id, "active": True, "plan_id": payload.subscription_id}
