# app/routes/selection_session.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.selection_session import SelectionJoinRequest, SelectionSessionCreate, SelectionSessionRead, SelectionJoinResponse
from app.schemas.selection import SelectMembersRequest, SelectionResult, MemberSelectionDetail
from app.services.selection_service import (
    create_selection_session, validate_code_and_get_fields, join_group,
    select_members, get_selected_members, clear_selections
)
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from typing import List


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


@router.post("/join", response_model=SelectionJoinResponse)
async def join_group_with_code(payload: SelectionJoinRequest, session: SessionDep):
    try:
        return await join_group(
            code=payload.code,
            member_identifier=payload.member_identifier,
            member_data=payload.member_data,
            session=session
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/select", response_model=SelectionResult)
async def perform_member_selection(
    data: SelectMembersRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Select members from a session based on count and preferential criteria.
    Only the host who created the session can perform this operation.
    """
    try:
        return await select_members(data, current_user.id, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/selected", response_model=List[MemberSelectionDetail])
async def get_all_selected_members(
    code: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get all selected members for a session.
    Only the host who created the session can perform this operation.
    """
    try:
        return await get_selected_members(code, current_user.id, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/clear")
async def clear_all_selections(
    code: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Clear all selections for a session.
    Only the host who created the session can perform this operation.
    """
    try:
        cleared_count = await clear_selections(code, current_user.id, session)
        return {"message": f"Successfully cleared {cleared_count} selections"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
