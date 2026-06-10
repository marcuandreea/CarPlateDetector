from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Cererea pentru înregistrarea unui nou utilizator
class UserRegisterRequest(BaseModel):
    nume: str = Field(min_length=1, max_length=100)
    prenume: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    numar_inmatriculare: str = Field(min_length=1, max_length=20)


# Cererea pentru autentificare a unui utilizator
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

# Raspunsul pentru profilul unui utilizator
class UserProfileResponse(BaseModel):
    id: int
    nume: str
    prenume: str
    email: EmailStr
    numar_inmatriculare: str
    qr_path: Optional[str] = None

# Cererea pentru actualizarea profilului unui utilizator
class UserProfileUpdateRequest(BaseModel):
    nume: Optional[str] = Field(default=None, min_length=1, max_length=100)
    prenume: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    numar_inmatriculare: Optional[str] = Field(default=None, min_length=1, max_length=20)
