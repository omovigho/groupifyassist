# app/routes/export.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from app.services.export_service import (
    validate_host_access, 
    generate_excel_for_session, 
    generate_pdf_for_session
)
from app.schemas.export import ExportOptions, ExportUrls
from typing import Optional
from io import BytesIO

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/group-session/{session_id}/excel")
async def export_group_session_excel(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export group session data as Excel file. Only the host can export their own sessions."""
    # Validate host has permission to access this session
    is_valid = await validate_host_access(
        session_id=session_id,
        session_type="group",
        host_id=current_user.id,
        access_code=access_code,
        db=session
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session or the access code is invalid"
        )
    
    try:
        # Generate Excel file
        file_buffer, metadata = await generate_excel_for_session(session_id, "group", session)
        
        # Return the Excel file
        filename = f"group_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.xlsx"
        
        return StreamingResponse(
            file_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )


@router.get("/group-session/{session_id}/pdf")
async def export_group_session_pdf(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export group session data as PDF file. Only the host can export their own sessions."""
    # Validate host has permission to access this session
    is_valid = await validate_host_access(
        session_id=session_id,
        session_type="group",
        host_id=current_user.id,
        access_code=access_code,
        db=session
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session or the access code is invalid"
        )
    
    try:
        # Generate PDF file
        file_buffer, metadata = await generate_pdf_for_session(session_id, "group", session)
        
        # Return the PDF file
        filename = f"group_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.pdf"
        
        return StreamingResponse(
            file_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF file: {str(e)}"
        )


@router.get("/selection-session/{session_id}/excel")
async def export_selection_session_excel(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export selection session data as Excel file. Only the host can export their own sessions."""
    # Validate host has permission to access this session
    is_valid = await validate_host_access(
        session_id=session_id,
        session_type="selection",
        host_id=current_user.id,
        access_code=access_code,
        db=session
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session or the access code is invalid"
        )
    
    try:
        # Generate Excel file
        file_buffer, metadata = await generate_excel_for_session(session_id, "selection", session)
        
        # Return the Excel file
        filename = f"selection_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.xlsx"
        
        return StreamingResponse(
            file_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )


@router.get("/selection-session/{session_id}/pdf")
async def export_selection_session_pdf(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    session: SessionDep = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export selection session data as PDF file. Only the host can export their own sessions."""
    # Validate host has permission to access this session
    is_valid = await validate_host_access(
        session_id=session_id,
        session_type="selection",
        host_id=current_user.id,
        access_code=access_code,
        db=session
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session or the access code is invalid"
        )
    
    try:
        # Generate PDF file
        file_buffer, metadata = await generate_pdf_for_session(session_id, "selection", session)
        
        # Return the PDF file
        filename = f"selection_session_{metadata['session_name'].replace(' ', '_')}_{session_id}.pdf"
        
        return StreamingResponse(
            file_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF file: {str(e)}"
        )

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
