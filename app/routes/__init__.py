# app/routes/__init__.py
from fastapi import APIRouter
from .user import router as auth_router
from .group_session import router as group_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(group_router)