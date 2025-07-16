# app/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
from app.models import User
from app.core.database import get_session
from app.core.cache import store_temp_user, get_temp_user, delete_temp_user, set_cache, get_cache, delete_cache
from app.core.database import SessionDep
from app.utils.email_utils import send_email, generate_code
from app.utils.email_template import registration_message, registration_success
from app.schemas.user import RegisterRequest, RegisterResponse, RegistrationVerificationRequest
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest


router = APIRouter(prefix="/api/user", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

'''@router.post("/sign-up", response_model=RegisterResponse)
async def register_user(request: RegisterRequest, session: SessionDep):
    existing = await session.exec(select(User).where(User.email == request.email))
    if existing.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    user = User(
        email=request.email,
        password=pwd_context.hash(request.password),
        country=request.country,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "Registration successful"}'''


@router.post("/sign-up", )
async def request_email_verification(request: RegisterRequest, session: SessionDep):
    email = request.email
    existing = await session.exec(select(User).where(User.email == request.email))
    if existing.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if not request.country:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country is required")
    
    # Store user data temporarily
    store_temp_user(email, {
        "email": email,
        "password": pwd_context.hash(request.password),  # hash immediately
        "country": request.country
    }, 60)

    # Send code
    code = generate_code()
    set_cache(f"verify_code_{email}", code, timeout=60)

    send_email(
        to_email=email,
        subject="Verify Your Email",
        body=registration_message(code=code, year=2025)
    )

    return {"message": "Verification code sent to your email"}


@router.post("/email-confirmation")
async def verify_user(request: RegistrationVerificationRequest, session: SessionDep):
    stored_code = get_cache(f"verify_code_{request.email}")
    if stored_code != request.code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user_data = get_temp_user(request.email)
    if not user_data:
        raise HTTPException(status_code=400, detail="User data expired or missing")

    send_email(
        to_email=request.email,
        subject="Registration Successful",
        body=registration_success(year=2025, email=request.email)
    )
    # Create user in DB
    user = User(**user_data)
    session.add(user)
    await session.commit()

    # Clean up
    delete_cache(f"verify_code_{request.email}")
    delete_temp_user(request.email)

    return {"message": "User verified and registered successfully"}


# app/routes/auth.py


@router.post("/login")
async def login(request: LoginRequest, session: SessionDep):
    use= await session.exec(select(User).where(User.email == request.email))
    user = use.first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }
