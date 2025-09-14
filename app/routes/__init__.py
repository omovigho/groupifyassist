# app/routes/__init__.py
from fastapi import APIRouter
from app.routes.user import router as auth_router
from app.routes.group_session import router as group_router
from app.routes.selection_session import router as selection_router
from app.routes.export import router as export_router
from app.routes.dashboard import router as dashboard_router
from app.routes.realtime import router as realtime_router
from app.routes.settings import router as settings_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(group_router)
router.include_router(selection_router)
router.include_router(export_router)
router.include_router(dashboard_router)
router.include_router(realtime_router)
router.include_router(settings_router)