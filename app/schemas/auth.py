from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserProfileResponse(BaseModel):
    id: int
    email: str
    country: str
    is_active: bool
    created_at: datetime
