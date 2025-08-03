# app/routes/export_additions.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import SessionDep
from app.core.dependencies import get_current_user
from app.models.user import User
from app.routes.export import export_selection_session_excel, export_selection_session_pdf, export_group_session_excel, export_group_session_pdf

router = APIRouter()

@router.get("/selection-session/{session_id}")
async def export_selection_session_options(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    format: str = Query(..., description="Format of the export: 'excel', 'pdf', or 'both'"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export selection session data in chosen format(s). Only the host can export their own sessions."""
    if format not in ["excel", "pdf", "both"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format specified. Use 'excel', 'pdf', or 'both'"
        )
    
    # For 'both' format, redirect to individual endpoints
    if format == "both":
        return {
            "message": "Use individual endpoints for each format",
            "excel_url": f"/api/export/selection-session/{session_id}/excel?access_code={access_code}",
            "pdf_url": f"/api/export/selection-session/{session_id}/pdf?access_code={access_code}"
        }
    
    # For specific formats, redirect to the appropriate endpoint
    if format == "excel":
        return await export_selection_session_excel(session_id, access_code, session, current_user)
    else:  # pdf
        return await export_selection_session_pdf(session_id, access_code, session, current_user)


@router.get("/group-session/{session_id}")
async def export_group_session_options(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    format: str = Query(..., description="Format of the export: 'excel', 'pdf', or 'both'"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export group session data in chosen format(s). Only the host can export their own sessions."""
    if format not in ["excel", "pdf", "both"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format specified. Use 'excel', 'pdf', or 'both'"
        )
    
    # For 'both' format, redirect to individual endpoints
    if format == "both":
        return {
            "message": "Use individual endpoints for each format",
            "excel_url": f"/api/export/group-session/{session_id}/excel?access_code={access_code}",
            "pdf_url": f"/api/export/group-session/{session_id}/pdf?access_code={access_code}"
        }
    
    # For specific formats, redirect to the appropriate endpoint
    if format == "excel":
        return await export_group_session_excel(session_id, access_code, session, current_user)
    else:  # pdf
        return await export_group_session_pdf(session_id, access_code, session, current_user)
