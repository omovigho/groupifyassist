from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Cookie
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM
import os

# For OpenAPI docs; actual verification uses Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", auto_error=False)

AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "access_token")


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    access_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Prefer Authorization header; fall back to HttpOnly cookie
    tok = token or access_cookie
    if not tok:
        raise credentials_exception

    try:
        payload = jwt.decode(tok, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    result = await session.exec(select(User).where(User.email == email))
    user = result.first()
    if user is None:
        raise credentials_exception

    return user
