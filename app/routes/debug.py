# app/routes/debug.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from app.core.dependencies import get_current_user
from app.models.user import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode

router = APIRouter(prefix="/api/debug", tags=["Debug"])

@router.get("/session/{session_id}")
async def check_session_access(
    session_id: int,
    access_code: str = Query(..., description="Access code to check"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Debug endpoint to check if you have permission to access a session"""
    
    # Get session info
    result = await session.exec(
        select(SelectionSession, AccessCode)
        .where(
            (SelectionSession.id == session_id) &
            (SelectionSession.code_id == AccessCode.id)
        )
    )
    session_data = result.first()
    
    if not session_data:
        return {
            "found": False,
            "message": f"Session with ID {session_id} not found",
            "your_user_id": current_user.id
        }
    
    selection_session, session_access_code = session_data
    
    return {
        "found": True,
        "session_id": selection_session.id,
        "session_name": selection_session.name,
        "session_host_id": selection_session.host_id,
        "your_user_id": current_user.id,
        "are_you_host": selection_session.host_id == current_user.id,
        "access_code_in_db": session_access_code.code,
        "access_code_provided": access_code,
        "access_code_matches": session_access_code.code == access_code,
        "all_conditions_met": (
            selection_session.host_id == current_user.id and 
            session_access_code.code == access_code
        )
    }
