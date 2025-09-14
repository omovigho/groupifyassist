# app/routes/auth.py
from fastapi import APIRouter, Depends, Response, Cookie
from app.core.database import SessionDep
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.user_service import AuthService
from app.schemas.user import (
    RegisterRequest,
    LoginRequest, LoginResponse,
    ChangePasswordRequest, UserProfileResponse, VerificationCodeRequest,
    ForgotPasswordStartRequest, ForgotPasswordResetRequest
)
from app.core.verify_session import COOKIE_NAME

router = APIRouter(prefix="/api/user", tags=["Authentication"])

@router.post("/sign-up", response_model=dict)
async def request_email_verification(request: RegisterRequest, session: SessionDep, response: Response):
    """
    Request email verification for user registration
    """
    return await AuthService.request_email_verification(request, session, response)

@router.post("/email-confirmation", response_model=dict)
async def verify_user_registration(request: VerificationCodeRequest, session: SessionDep, response: Response, vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    """
    Verify user registration with email verification code
    """
    return await AuthService.verify_user_registration(request.code, session, response, vsid)

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: SessionDep, response: Response):
    """
    Authenticate user and return access token, plus set HttpOnly cookie.
    """
    return await AuthService.login_user(request, session, response)

@router.post("/resend-verification", response_model=dict)
async def resend_verification_code(session: SessionDep, response: Response, vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    """
    Resend verification code for email verification
    """
    return await AuthService.resend_verification_code(vsid, session, response)

@router.get("/verification/session", response_model=dict)
async def get_verification_session_info(vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    return await AuthService.get_verification_session_info(vsid)


# Forgot password flow
@router.post("/forgot-password/start", response_model=dict)
async def forgot_password_start(request: ForgotPasswordStartRequest, session: SessionDep, response: Response):
    return await AuthService.forgot_password_start(request.email, session, response)


@router.post("/forgot-password/verify", response_model=dict)
async def forgot_password_verify(request: VerificationCodeRequest, session: SessionDep, response: Response, vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    return await AuthService.forgot_password_verify(request.code, session, response, vsid)


@router.post("/forgot-password/resend", response_model=dict)
async def forgot_password_resend(session: SessionDep, response: Response, vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    return await AuthService.forgot_password_resend(vsid, session, response)


@router.post("/forgot-password/reset", response_model=dict)
async def forgot_password_reset(request: ForgotPasswordResetRequest, session: SessionDep, response: Response, vsid: str | None = Cookie(default=None, alias=COOKIE_NAME)):
    return await AuthService.forgot_password_reset(request.new_password, session, response, vsid)

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
async def logout(response: Response, _: User = Depends(get_current_user)):
    # Clear auth cookie
    import os
    from app.core.verify_session import COOKIE_PATH_API, COOKIE_DOMAIN
    auth_cookie_name = os.getenv("AUTH_COOKIE_NAME", "access_token")
    response.delete_cookie(key=auth_cookie_name, path=COOKIE_PATH_API, domain=COOKIE_DOMAIN or None)
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
