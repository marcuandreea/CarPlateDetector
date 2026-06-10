from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user_id
from models.user import (
    UserLoginRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserRegisterRequest,
)
from services.user_service import get_profile, login_user, register_user, update_profile

router = APIRouter(tags=["users"])

# Endpoint pentru înregistrarea unui nou utilizator
@router.post("/register")
def register(payload: UserRegisterRequest):
    return register_user(payload)

# Endpoint pentru autentificarea unui utilizator și obținerea token-ului de acces
@router.post("/login")
def login(payload: UserLoginRequest):
    return login_user(payload)

# Endpoint pentru obținerea profilului utilizatorului curent 
@router.get("/profile", response_model=UserProfileResponse)
def profile(current_user_id: int = Depends(get_current_user_id)):
    return get_profile(current_user_id)

# Endpoint pentru actualizarea profilului utilizatorului curent
@router.put("/profile", response_model=UserProfileResponse)
def profile_update(
    payload: UserProfileUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    return update_profile(current_user_id, payload)
