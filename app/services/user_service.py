# app/services/auth_service.py
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
from app.models.user import User
from app.core.cache import store_temp_user, get_temp_user, delete_temp_user, set_cache, get_cache, delete_cache
from app.utils.email_utils import send_email, generate_code
from app.utils.email_template import registration_message, registration_success
from app.schemas.user import RegisterRequest, RegistrationVerificationRequest
from app.schemas.user import LoginRequest
from app.core.security import verify_password, create_access_token, mask_email
from typing import Dict, Any
from fastapi import Response
from app.core.verify_session import create_session, set_cookie, verify_code_for_session, delete_session, clear_cookie, get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    async def request_email_verification(request: RegisterRequest, session: AsyncSession, response: Response) -> Dict[str, str]:
        """
        Handle email verification request for user registration
        """
        email = request.email
        
        # Check if user already exists
        existing_user_query = await session.exec(select(User).where(User.email == email))
        existing_user = existing_user_query.first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        
        # Validate password confirmation
        if request.password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Passwords do not match"
            )
        
        # Validate country field
        if not request.country:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Country is required"
            )
        
        # Store user data temporarily (server-side only)
        user_data = {
            "email": email,
            "password": pwd_context.hash(request.password),  # Hash password immediately
            "country": request.country
        }
        store_temp_user(email, user_data, timeout=600)  # 10 minutes timeout
        
        # Generate and store verification code
        verification_code = generate_code()
        # Create a verification session bound to this email and code
        sid = create_session(email=email, purpose="register", code=verification_code)
        
        # Send verification email
        try:
            send_email(
                to_email=email,
                subject="Verify Your Email - GroupifyAssist",
                body=registration_message(code=verification_code, year=2025)
            )
        except Exception as e:
            # Clean up cache if email sending fails
            delete_temp_user(email)
            delete_session(sid)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )

        # Set HttpOnly cookie with the opaque session id
        set_cookie(response, sid, purpose="register")
        
        return {"message": "Verification code sent to your email"}
    
    @staticmethod
    async def verify_user_registration(code: str, session: AsyncSession, response: Response, vsid: str | None) -> Dict[str, str]:
        """
        Verify user registration with email verification code
        """
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        ok, err = verify_code_for_session(vsid, code)
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        sess = get_session(vsid)
        if not sess:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        email = sess["email"]

        # Retrieve temporary user data
        user_data = get_temp_user(email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User data expired or missing. Please restart registration process."
            )
        
        # Create user in database
        try:
            user = User(**user_data)
            user.is_active = True  # Activate user upon verification
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account. Please try again."
            )
        
        # Send success email
        try:
            send_email(
                to_email=email,
                subject="Welcome to GroupifyAssist!",
                body=registration_success(year=2025, email=email)
            )
        except Exception:
            # Don't fail registration if success email fails
            pass
        # Clean up temporary data and cookie
        delete_temp_user(email)
        delete_session(vsid)
        clear_cookie(response, purpose="register")

        return {"message": "User verified and registered successfully"}
    
    @staticmethod
    async def login_user(request: LoginRequest, session: AsyncSession) -> Dict[str, Any]:
        """
        Authenticate user and return access token
        """
        email = request.email
        password = request.password
        
        # Find user by email
        user_query = await session.exec(select(User).where(User.email == email))
        user = user_query.first()
        
        # Verify user exists and password is correct
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if user account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active. Please verify your email.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Generate access token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "country": user.country,
                "is_active": user.is_active
            }
        }
    
    @staticmethod
    async def resend_verification_code(vsid: str | None, session: AsyncSession, response: Response) -> Dict[str, str]:
        """
        Resend verification code for email verification
        """
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        sess = get_session(vsid)
        if not sess:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        email = sess["email"]
        # Check if user already exists
        existing_user_query = await session.exec(select(User).where(User.email == email))
        existing_user = existing_user_query.first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if temporary user data exists
        user_data = get_temp_user(email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending registration found for this email. Please restart registration."
            )
        
        # Generate new verification code
        verification_code = generate_code()
        # Recreate session with new code (rotate session id)
        delete_session(vsid)
        new_vsid = create_session(email=email, purpose="register", code=verification_code)
        
        # Send new verification email
        try:
            send_email(
                to_email=email,
                subject="Verify Your Email - GroupifyAssist",
                body=registration_message(code=verification_code, year=2025)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )
        # Update cookie
        set_cookie(response, new_vsid, purpose="register")
        
        return {"message": "New verification code sent to your email"}

    @staticmethod
    async def get_verification_session_info(vsid: str | None) -> Dict[str, Any]:
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        sess = get_session(vsid)
        if not sess:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        return {
            "email_masked": mask_email(sess["email"]),
            "purpose": sess.get("purpose"),
        }

    # Forgot password flow
    @staticmethod
    async def forgot_password_start(email: str, session: AsyncSession, response: Response) -> Dict[str, str]:
        # Ensure the user exists and is active
        user_query = await session.exec(select(User).where(User.email == email))
        user = user_query.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found with that email")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active. Please verify your email first.")
        code = generate_code()
        vsid = create_session(email=email, purpose="reset", code=code)
        try:
            send_email(
                to_email=email,
                subject="Reset your password - GroupifyAssist",
                body=registration_message(code=code, year=2025),
            )
        except Exception:
            delete_session(vsid)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send reset code. Please try again.")
        set_cookie(response, vsid, purpose="reset")
        return {"message": "Reset code sent to your email"}

    @staticmethod
    async def forgot_password_verify(code: str, session: AsyncSession, response: Response, vsid: str | None) -> Dict[str, str]:
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        ok, err = verify_code_for_session(vsid, code)
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        # Mark session as code-verified (optional). We'll keep vsid for reset step and short TTL.
        return {"message": "Code verified. You can now reset your password."}

    @staticmethod
    async def forgot_password_resend(vsid: str | None, session: AsyncSession, response: Response) -> Dict[str, str]:
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        sess = get_session(vsid)
        if not sess:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        email = sess["email"]
        code = generate_code()
        delete_session(vsid)
        new_vsid = create_session(email=email, purpose="reset", code=code)
        try:
            send_email(
                to_email=email,
                subject="Reset your password - GroupifyAssist",
                body=registration_message(code=code, year=2025),
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resend code.")
        set_cookie(response, new_vsid, purpose="reset")
        return {"message": "New code sent."}

    @staticmethod
    async def forgot_password_reset(new_password: str, session: AsyncSession, response: Response, vsid: str | None) -> Dict[str, str]:
        if not vsid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification session missing")
        sess = get_session(vsid)
        if not sess:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        email = sess["email"]
        # Update password
        user_query = await session.exec(select(User).where(User.email == email))
        user = user_query.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        try:
            user.password = pwd_context.hash(new_password)
            session.add(user)
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")
        delete_session(vsid)
        clear_cookie(response, purpose="reset")
        return {"message": "Password reset successfully"}
    
    @staticmethod
    async def get_user_profile(user_email: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Get user profile information
        """
        user_query = await session.exec(select(User).where(User.email == user_email))
        user = user_query.first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "country": user.country,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    
    @staticmethod
    async def change_password(user_email: str, current_password: str, new_password: str, session: AsyncSession) -> Dict[str, str]:
        """
        Change user password
        """
        # Find user
        user_query = await session.exec(select(User).where(User.email == user_email))
        user = user_query.first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        try:
            user.password = pwd_context.hash(new_password)
            session.add(user)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password. Please try again."
            )
        
        return {"message": "Password changed successfully"}
