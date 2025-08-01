# app/routes/group_session.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.selection_session import SelectionSessionCreate, SelectionSessionRead
from app.services.selection_service import create_selection_session
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User


router = APIRouter(prefix="/api/selections", tags=["Selection"])

@router.post("/create", response_model=SelectionSessionRead)
async def create_selection(
    data: SelectionSessionCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    try:
        selection = await create_selection_session(data, current_user.id, session)
        return selection
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
