from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import os
import hashlib
from typing import Optional

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Use bcrypt_sha256 to avoid the 72 byte plaintext limit while keeping
# compatibility with existing bcrypt hashes.
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    default="bcrypt_sha256",
    deprecated="auto",
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def hash_verification_code(code: str, secret: Optional[str] = None) -> str:
    """
    Returns a stable SHA-256 hash for verification/reset codes using a server-side secret.
    """
    s = (secret or SECRET_KEY)
    # Mix the secret to avoid rainbow-table reuse across environments
    payload = (code + ":" + s).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def mask_email(email: str) -> str:
    """Return a lightly masked version like j***e@d***n.com"""
    try:
        local, domain = email.split("@", 1)
        def mask_piece(x: str) -> str:
            if len(x) <= 2:
                return x[0] + "*" * (len(x) - 1)
            return x[0] + "***" + x[-1]
        dmain, _, tld = domain.partition(".")
        masked_local = mask_piece(local)
        masked_domain = mask_piece(dmain)
        return f"{masked_local}@{masked_domain}.{tld}" if tld else f"{masked_local}@{masked_domain}"
    except Exception:
        return email
