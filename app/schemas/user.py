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


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    country: str


class RegistrationVerificationRequest(BaseModel):
    code: str


class RegisterResponse(BaseModel):
    message: str


class VerificationCodeRequest(BaseModel):
    code: str


class ForgotPasswordStartRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResetRequest(BaseModel):
    new_password: str
