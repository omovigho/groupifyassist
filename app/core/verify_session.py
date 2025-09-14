from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, TypedDict

from fastapi import Response
from app.core.cache import redis
from app.core.security import hash_verification_code


PURPOSE = Literal["register", "reset"]


class VerifySession(TypedDict, total=False):
    email: str
    purpose: PURPOSE
    code_hash: str
    created_at: str
    expires_at: str
    attempts: int


SESSION_TTL_SECONDS = int(os.getenv("VERIFY_SESSION_TTL", "900"))  # 15 minutes
COOKIE_NAME = os.getenv("VERIFY_SESSION_COOKIE", "vsid")
COOKIE_PATH_API = "/api"  # scope to backend API routes so cookie is sent with API calls

# Heuristic to detect production hosting environments
_ENV = os.getenv("ENV", os.getenv("ENVIRONMENT", "")).lower()
_IS_PROD = (
    _ENV in {"prod", "production"}
    or os.getenv("VERCEL", "") == "1"
    or os.getenv("RENDER", "").lower() == "true"
    or os.getenv("RAILWAY_ENVIRONMENT", "") != ""
)

# Defaults: dev uses lax/insecure, prod uses none/secure (required for cross-site cookies)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true" if _IS_PROD else "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "none" if _IS_PROD else "lax").lower()  # lax | none | strict

# Optional cookie domain override (e.g., api.example.com). Leave unset to let the browser default.
COOKIE_DOMAIN = os.getenv("VERIFY_COOKIE_DOMAIN")


def _session_key(sid: str) -> str:
    return f"verify:session:{sid}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.isoformat()


def create_session(email: str, purpose: PURPOSE, code: str) -> str:
    sid = secrets.token_urlsafe(24)
    now = _now()
    exp = now + timedelta(seconds=SESSION_TTL_SECONDS)
    data: VerifySession = {
        "email": email,
        "purpose": purpose,
        "code_hash": hash_verification_code(code),
        "created_at": _to_iso(now),
        "expires_at": _to_iso(exp),
        "attempts": 0,
    }
    redis.set(_session_key(sid), json.dumps(data), ex=SESSION_TTL_SECONDS)
    return sid


def get_session(sid: str) -> Optional[VerifySession]:
    raw = redis.get(_session_key(sid))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def update_session(sid: str, data: dict) -> None:
    key = _session_key(sid)
    raw = redis.get(key)
    if not raw:
        return
    try:
        obj = json.loads(raw)
        obj.update(data)
        # preserve TTL by fetching remaining TTL and re-setting
        ttl = redis.pttl(key)
        # Upstash returns milliseconds; if -1 or -2, default to SESSION_TTL_SECONDS
        ex = max(1, int(ttl / 1000)) if isinstance(ttl, int) and ttl > 0 else SESSION_TTL_SECONDS
        redis.set(key, json.dumps(obj), ex=ex)
    except (json.JSONDecodeError, TypeError, ValueError):
        return


def delete_session(sid: str) -> None:
    redis.delete(_session_key(sid))


def set_cookie(response: Response, sid: str, purpose: PURPOSE) -> None:
    _ = purpose  # silence unused param; kept for future purpose-based scoping
    path = COOKIE_PATH_API
    same_site = "lax" if COOKIE_SAMESITE not in {"lax", "none", "strict"} else COOKIE_SAMESITE
    # Browsers require Secure when SameSite=None; enforce at runtime to avoid silent drops
    secure_flag = COOKIE_SECURE or (same_site == "none")
    response.set_cookie(
        key=COOKIE_NAME,
        value=sid,
        max_age=SESSION_TTL_SECONDS,
        path=path,
        secure=secure_flag,
        httponly=True,
    samesite="none" if same_site == "none" else ("strict" if same_site == "strict" else "lax"),
        domain=COOKIE_DOMAIN if COOKIE_DOMAIN else None,
    )


def clear_cookie(response: Response, purpose: PURPOSE) -> None:
    _ = purpose  # silence unused param; kept for future purpose-based scoping
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH_API)


def verify_code_for_session(sid: str, input_code: str, max_attempts: int = 5) -> tuple[bool, Optional[str]]:
    sess = get_session(sid)
    if not sess:
        return False, "Session expired. Please restart."
    attempts = int(sess.get("attempts", 0)) + 1
    if attempts > max_attempts:
        delete_session(sid)
        return False, "Too many attempts. Please restart."
    update_session(sid, {"attempts": attempts})
    ok = hash_verification_code(input_code) == sess.get("code_hash")
    if not ok:
        return False, "Invalid code."
    return True, None
