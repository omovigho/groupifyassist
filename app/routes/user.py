# app/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import SessionDep
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.user_service import AuthService
from app.schemas.user import (
    RegisterRequest, RegisterResponse, RegistrationVerificationRequest,
    LoginRequest, LoginResponse, ResendVerificationRequest, 
    ChangePasswordRequest, UserProfileResponse
)

router = APIRouter(prefix="/api/user", tags=["Authentication"])

@router.post("/sign-up", response_model=dict)
async def request_email_verification(request: RegisterRequest, session: SessionDep):
    """
    Request email verification for user registration
    """
    return await AuthService.request_email_verification(request, session)

@router.post("/email-confirmation", response_model=dict)
async def verify_user_registration(request: RegistrationVerificationRequest, session: SessionDep):
    """
    Verify user registration with email verification code
    """
    return await AuthService.verify_user_registration(request, session)

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: SessionDep):
    """
    Authenticate user and return access token
    """
    return await AuthService.login_user(request, session)

@router.post("/resend-verification", response_model=dict)
async def resend_verification_code(request: ResendVerificationRequest, session: SessionDep):
    """
    Resend verification code for email verification
    """
    return await AuthService.resend_verification_code(request.email, session)

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(session: SessionDep, current_user: User = Depends(get_current_user)):
    """
    Get current user profile information
    """
    return await AuthService.get_user_profile(current_user.email, session)

@router.put("/change-password", response_model=dict)
async def change_password(
    request: ChangePasswordRequest, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)
):
    """
    Change user password
    """
    return await AuthService.change_password(
        current_user.email, 
        request.current_password, 
        request.new_password, 
        session
    )

@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

@router.get("/verify-token", response_model=dict)
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if the current token is valid
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "country": current_user.country,
            "is_active": current_user.is_active
        }
    }
