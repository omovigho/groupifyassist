# app/schemas/export.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ExportOptions(BaseModel):
    """Options for exporting session data"""
    session_id: int
    access_code: str
    format: str  # 'excel', 'pdf', or 'both'


class ExportUrls(BaseModel):
    """URLs for downloading exported files"""
    message: str
    excel_url: Optional[str] = None
    pdf_url: Optional[str] = None
