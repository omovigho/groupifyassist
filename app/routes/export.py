# app/routes/export.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
import os
from pathlib import Path
from app.core.dependencies import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.services.export_service import (
    validate_host_access, 
    generate_excel_for_session, 
    generate_pdf_for_session
)
from app.utils.file_saver import save_export_file
from app.utils.export_helpers import process_file_export
from app.schemas.export import ExportOptions, ExportUrls
from typing import Optional
from io import BytesIO

router = APIRouter(prefix="/api/export", tags=["Export"])

# Define export directories as constants to ensure consistency
EXCEL_EXPORTS_DIR = "C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/excel_exports"
PDF_EXPORTS_DIR = "C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/pdf_exports"

# Create directories if they don't exist
Path(EXCEL_EXPORTS_DIR).mkdir(parents=True, exist_ok=True)
Path(PDF_EXPORTS_DIR).mkdir(parents=True, exist_ok=True)

@router.get("/check-export-directories")
async def check_export_directories(current_user: User = Depends(get_current_user)):
    """Check if export directories exist and are writable"""
    result = {
        "excel_exports": {
            "path": EXCEL_EXPORTS_DIR,
            "exists": os.path.exists(EXCEL_EXPORTS_DIR),
            "writable": os.access(EXCEL_EXPORTS_DIR, os.W_OK) if os.path.exists(EXCEL_EXPORTS_DIR) else False,
            "files": []
        },
        "pdf_exports": {
            "path": PDF_EXPORTS_DIR,
            "exists": os.path.exists(PDF_EXPORTS_DIR),
            "writable": os.access(PDF_EXPORTS_DIR, os.W_OK) if os.path.exists(PDF_EXPORTS_DIR) else False,
            "files": []
        }
    }
    
    # List existing files
    if result["excel_exports"]["exists"]:
        result["excel_exports"]["files"] = [f for f in os.listdir(EXCEL_EXPORTS_DIR) if f.endswith('.xlsx')][:10]  # Limit to 10 files
        
    if result["pdf_exports"]["exists"]:
        result["pdf_exports"]["files"] = [f for f in os.listdir(PDF_EXPORTS_DIR) if f.endswith('.pdf')][:10]  # Limit to 10 files
    
    return JSONResponse(content=result)

@router.get("/check-export-directories")
async def check_export_directories(current_user: User = Depends(get_current_user)):
    """Check if export directories exist and are writable"""
    import os
    
    # Define directories to check
    base_dir = "C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist"
    directories = {
        "excel_exports": os.path.join(base_dir, "excel_exports"),
        "pdf_exports": os.path.join(base_dir, "pdf_exports")
    }
    
    results = {}
    for name, dir_path in directories.items():
        # Check if directory exists
        exists = os.path.exists(dir_path)
        
        # Create if it doesn't exist
        if not exists:
            try:
                os.makedirs(dir_path, exist_ok=True)
                exists = True
            except Exception as e:
                results[name] = {
                    "exists": False,
                    "writable": False,
                    "error": str(e)
                }
                continue
        
        # Check if writable
        writable = False
        try:
            test_file = os.path.join(dir_path, "write_test.txt")
            with open(test_file, 'w') as f:
                f.write("Write test")
            os.remove(test_file)
            writable = True
        except Exception as e:
            results[name] = {
                "exists": exists,
                "writable": False,
                "error": str(e)
            }
            continue
        
        # List any existing files in directory
        files = []
        try:
            files = os.listdir(dir_path)
        except Exception as e:
            pass
        
        results[name] = {
            "exists": exists,
            "writable": writable,
            "files": files[:10] if len(files) > 10 else files,  # Limit number of files returned
            "file_count": len(files),
            "path": dir_path
        }
    
    return {
        "status": "success",
        "directories": results
    }


@router.get("/group-session/{session_id}/excel")
async def export_group_session_excel(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        # Generate the Excel file
        file_buffer, metadata = await generate_excel_for_session(
            session_id, 
            "group", 
            session,
            save_to_disk=False  # We'll handle saving manually
        )
        
        # Process the export using our helper
        response, _ = process_file_export(
            file_buffer=file_buffer,
            session_type="group",
            session_id=session_id,
            metadata=metadata,
            file_extension="xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            save_directory=EXCEL_EXPORTS_DIR,
            host_info={"id": current_user.id, "email": current_user.email}
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )


@router.get("/group-session/{session_id}/pdf")
async def export_group_session_pdf(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        # Generate the PDF file
        file_buffer, metadata = await generate_pdf_for_session(
            session_id, 
            "group", 
            session,
            save_to_disk=False  # We'll handle saving manually
        )
        
        # Process the export using our helper
        response, _ = process_file_export(
            file_buffer=file_buffer,
            session_type="group",
            session_id=session_id,
            metadata=metadata,
            file_extension="pdf",
            media_type="application/pdf",
            save_directory=PDF_EXPORTS_DIR,
            host_info={"id": current_user.id, "email": current_user.email}
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF file: {str(e)}"
        )


@router.get("/selection-session/{session_id}/excel")
async def export_selection_session_excel(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        # Generate the Excel file
        file_buffer, metadata = await generate_excel_for_session(
            session_id, 
            "selection", 
            session,
            save_to_disk=False  # We'll handle saving manually
        )
        
        # Process the export using our helper
        response, _ = process_file_export(
            file_buffer=file_buffer,
            session_type="selection",
            session_id=session_id,
            metadata=metadata,
            file_extension="xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            save_directory=EXCEL_EXPORTS_DIR,
            host_info={"id": current_user.id, "email": current_user.email}
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )


@router.get("/selection-session/{session_id}/pdf")
async def export_selection_session_pdf(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        # Generate the PDF file
        file_buffer, metadata = await generate_pdf_for_session(
            session_id, 
            "selection", 
            session,
            save_to_disk=False  # We'll handle saving manually
        )
        
        # Process the export using our helper
        response, _ = process_file_export(
            file_buffer=file_buffer,
            session_type="selection",
            session_id=session_id,
            metadata=metadata,
            file_extension="pdf",
            media_type="application/pdf",
            save_directory=PDF_EXPORTS_DIR,
            host_info={"id": current_user.id, "email": current_user.email}
        )
        
        return response
        
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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        return await export_selection_session_excel(session_id, access_code, current_user, session)
    else:  # pdf
        return await export_selection_session_pdf(session_id, access_code, current_user, session)


@router.get("/group-session/{session_id}")
async def export_group_session_options(
    session_id: int,
    access_code: str = Query(..., description="Access code for the session"),
    format: str = Query(..., description="Format of the export: 'excel', 'pdf', or 'both'"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
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
        return await export_group_session_excel(session_id, access_code, current_user, session)
    else:  # pdf
        return await export_group_session_pdf(session_id, access_code, current_user, session)
