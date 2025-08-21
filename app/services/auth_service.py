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
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token
from typing import Dict, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    async def request_email_verification(request: RegisterRequest, session: AsyncSession) -> Dict[str, str]:
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
        
        # Store user data temporarily
        user_data = {
            "email": email,
            "password": pwd_context.hash(request.password),  # Hash password immediately
            "country": request.country
        }
        store_temp_user(email, user_data, timeout=600)  # 10 minutes timeout
        
        # Generate and store verification code
        verification_code = generate_code()
        set_cache(f"verify_code_{email}", verification_code, timeout=600)  # 10 minutes timeout
        
        # Send verification email
        try:
            send_email(
                to_email=email,
                subject="Verify Your Email - GroupifyAssist",
                body=registration_message(code=verification_code, year=2025)
            )
        except Exception as e:
            # Clean up cache if email sending fails
            delete_cache(f"verify_code_{email}")
            delete_temp_user(email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )
        
        return {"message": "Verification code sent to your email"}
    
    @staticmethod
    async def verify_user_registration(request: RegistrationVerificationRequest, session: AsyncSession) -> Dict[str, str]:
        """
        Verify user registration with email verification code
        """
        email = request.email
        provided_code = request.code
        
        # Verify the code
        stored_code = get_cache(f"verify_code_{email}")
        if not stored_code or stored_code != provided_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid or expired verification code"
            )
        
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
        
        # Clean up temporary data
        delete_cache(f"verify_code_{email}")
        delete_temp_user(email)
        
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
    async def resend_verification_code(email: str, session: AsyncSession) -> Dict[str, str]:
        """
        Resend verification code for email verification
        """
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
        set_cache(f"verify_code_{email}", verification_code, timeout=600)
        
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
        
        return {"message": "New verification code sent to your email"}
    
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
