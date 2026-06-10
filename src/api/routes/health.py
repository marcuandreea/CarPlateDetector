from fastapi import APIRouter

from services.health_service import build_health_payload

router = APIRouter(tags=["health"])

# Endpoint pentru verificarea starii API-ului
@router.get("/health")
def health_check():
    return build_health_payload()
