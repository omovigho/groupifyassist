# app/routes/group_session.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead
from app.services.group_session_service import create_group_session
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from app.services.group_session_service import validate_code_and_get_fields, join_group
from app.schemas.group_session import GroupJoinRequest, GroupJoinResponse
from app.schemas.group_session import MessageResponse


router = APIRouter(prefix="/api/groups", tags=["Grouping"])


@router.post("/create", response_model=GroupSessionRead)
async def create_group(
    data: GroupSessionCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    try:
        group = await create_group_session(data, current_user.id, session)
        return group
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/fields", response_model=dict)
async def get_fields_for_code(code: str, session: SessionDep):
    try:
        return await validate_code_and_get_fields(code, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/join", response_model=GroupJoinResponse)
async def join_group_with_code(payload: GroupJoinRequest, session: SessionDep):
    try:
        return await join_group(
            code=payload.code,
            member_identifier=payload.member_identifier,
            member_data=payload.member_data,
            session=session
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
