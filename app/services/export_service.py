# app/services/export_service.py
from io import BytesIO
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List, Dict, Any, Tuple

from app.models.group_session import GroupSession
from app.models.selection_session import SelectionSession
from app.models.groups import Group
from app.models.group_member import GroupMember
from app.models.access_code import AccessCode
from app.models.selection_member import SelectionMember

import pandas as pd
from fpdf import FPDF


async def validate_host_access(
    session_id: int, 
    session_type: str,
    host_id: int, 
    access_code: str,
    db: AsyncSession
) -> bool:
    """Validate that the requesting user is the host of the session and the access code is correct"""
    # Determine which model to query based on session type
    if session_type == "group":
        model = GroupSession
    elif session_type == "selection":
        model = SelectionSession
    else:
        return False
    
    # Query the session
    result = await db.exec(
        select(model, AccessCode)
        .where(
            (model.id == session_id) &
            (model.host_id == host_id) &
            (model.code_id == AccessCode.id) &
            (AccessCode.code == access_code)
        )
    )
    
    session_data = result.first()
    return session_data is not None


async def generate_excel_for_session(
    session_id: int,
    session_type: str,
    db: AsyncSession
) -> Tuple[BytesIO, Dict[str, Any]]:
    """Generate Excel file for the given session type"""
    buffer = BytesIO()
    
    # Get session data based on session type
    if session_type == "group":
        session_data = await get_group_session_data(session_id, db)
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Session info sheet
            pd.DataFrame([{
                "Name": session_data["session"].name,
                "Description": session_data["session"].description,
                "Access Code": session_data["access_code"].code,
                "Max Group Size": session_data["session"].max_group_size,
                "Status": session_data["session"].status,
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]).to_excel(writer, sheet_name="Session Info", index=False)
            
            # Group members sheet
            groups_df = pd.DataFrame([
                {
                    "Group Name": group.name,
                    "Member Name": member.name,
                    "Member ID": member.member_id,
                    **({f"Field {i+1}": value for i, value in enumerate(member.fields.split(","))} if member.fields else {})
                }
                for group in session_data["groups"]
                for member in session_data["members"] if member.group_id == group.id
            ])
            
            if not groups_df.empty:
                groups_df.to_excel(writer, sheet_name="Group Members", index=False)
            
            # Format the sheets for better readability
            workbook = writer.book
            for worksheet in writer.sheets.values():
                worksheet.set_column(0, 10, 15)
        
        # Return the file buffer and session metadata
        return buffer, {
            "session_name": session_data["session"].name,
            "session_description": session_data["session"].description
        }
        
    elif session_type == "selection":
        session_data = await get_selection_session_data(session_id, db)
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Session info sheet
            pd.DataFrame([{
                "Name": session_data["session"].name,
                "Description": session_data["session"].description,
                "Access Code": session_data["access_code"].code,
                "Max Group Size": session_data["session"].max_group_size,
                "Created At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]).to_excel(writer, sheet_name="Session Info", index=False)
            
            # Selection members sheet
            members_df = pd.DataFrame([
                {
                    "Member ID": member.member_identifier,
                    "Selected": member.selected,
                    "Joined At": member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else None,
                    **(({k: v for k, v in member.attributes.items()}) if member.attributes else {})
                }
                for member in session_data["members"]
            ])
            
            if not members_df.empty:
                members_df.to_excel(writer, sheet_name="Selection Members", index=False)
            
            # Format the sheets for better readability
            workbook = writer.book
            for worksheet in writer.sheets.values():
                worksheet.set_column(0, 10, 15)
        
        # Return the file buffer and session metadata
        return buffer, {
            "session_name": session_data["session"].name,
            "session_description": session_data["session"].description
        }
    
    else:
        raise ValueError(f"Unknown session type: {session_type}")


async def generate_pdf_for_session(
    session_id: int,
    session_type: str,
    db: AsyncSession
) -> Tuple[BytesIO, Dict[str, Any]]:
    """Generate PDF file for the given session type"""
    buffer = BytesIO()
    
    # Get session data based on session type
    if session_type == "group":
        session_data = await get_group_session_data(session_id, db)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set up title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Group Session: {session_data['session'].name}", ln=True, align="C")
        
        # Session details
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Description: {session_data['session'].description}", ln=True)
        pdf.cell(0, 10, f"Access Code: {session_data['access_code'].code}", ln=True)
        pdf.cell(0, 10, f"Max Group Size: {session_data['session'].max_group_size}", ln=True)
        pdf.cell(0, 10, f"Status: {session_data['session'].status}", ln=True)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        
        # Group information
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Groups and Members", ln=True)
        
        # Loop through each group
        for group in session_data["groups"]:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Group: {group.name}", ln=True)
            
            # Table header
            pdf.set_font("Arial", "B", 11)
            pdf.cell(40, 10, "Member ID", border=1)
            pdf.cell(50, 10, "Member Name", border=1)
            pdf.cell(100, 10, "Fields", border=1)
            pdf.ln()
            
            # List members in this group
            pdf.set_font("Arial", "", 11)
            for member in [m for m in session_data["members"] if m.group_id == group.id]:
                pdf.cell(40, 10, member.member_id, border=1)
                pdf.cell(50, 10, member.name, border=1)
                pdf.cell(100, 10, member.fields or "N/A", border=1)
                pdf.ln()
            
            pdf.ln(5)
        
    elif session_type == "selection":
        session_data = await get_selection_session_data(session_id, db)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set up title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Selection Session: {session_data['session'].name}", ln=True, align="C")
        
        # Session details
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Description: {session_data['session'].description or 'N/A'}", ln=True)
        pdf.cell(0, 10, f"Access Code: {session_data['access_code'].code}", ln=True)
        pdf.cell(0, 10, f"Max Group Size: {session_data['session'].max_group_size}", ln=True)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        
        # Member information
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Selection Members", ln=True)
        
        # Table header
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 10, "Member ID", border=1)
        pdf.cell(30, 10, "Selected", border=1)
        pdf.cell(60, 10, "Joined Date", border=1)
        pdf.cell(60, 10, "Attributes", border=1)
        pdf.ln()
        
        # List all members
        pdf.set_font("Arial", "", 11)
        for member in session_data["members"]:
            pdf.cell(40, 10, member.member_identifier, border=1)
            pdf.cell(30, 10, "Yes" if member.selected else "No", border=1)
            pdf.cell(60, 10, member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A", border=1)
            
            # Format attributes as string
            if member.attributes:
                attr_str = ", ".join([f"{k}: {v}" for k, v in member.attributes.items()])
                attr_str = attr_str[:30] + "..." if len(attr_str) > 30 else attr_str
            else:
                attr_str = "N/A"
                
            pdf.cell(60, 10, attr_str, border=1)
            pdf.ln()
    
    else:
        raise ValueError(f"Unknown session type: {session_type}")
        
    # Save PDF to buffer
    pdf.output(dest='S').encode('latin-1')
    buffer.seek(0)
    
    # Return the file buffer and session metadata
    return buffer, {
        "session_name": session_data["session"].name,
        "session_description": session_data["session"].description
    }


async def get_group_session_data(session_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get all data needed for a group session export"""
    # Get session information
    result = await db.exec(
        select(GroupSession, AccessCode)
        .where(
            (GroupSession.id == session_id) &
            (GroupSession.code_id == AccessCode.id)
        )
    )
    session_result = result.first()
    
    if not session_result:
        raise ValueError(f"Group session not found with ID: {session_id}")
    
    session, access_code = session_result
    
    # Get all groups for this session
    groups_result = await db.exec(
        select(Group)
        .where(Group.session_id == session_id)
    )
    groups = groups_result.all()
    
    # Get all members for these groups
    members_result = await db.exec(
        select(GroupMember)
        .where(GroupMember.group_id.in_([group.id for group in groups]))
    )
    members = members_result.all()
    
    return {
        "session": session,
        "access_code": access_code,
        "groups": groups,
        "members": members
    }


async def get_selection_session_data(session_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get all data needed for a selection session export"""
    # Get session information
    result = await db.exec(
        select(SelectionSession, AccessCode)
        .where(
            (SelectionSession.id == session_id) &
            (SelectionSession.code_id == AccessCode.id)
        )
    )
    session_result = result.first()
    
    if not session_result:
        raise ValueError(f"Selection session not found with ID: {session_id}")
    
    session, access_code = session_result
    
    # Get all members for this session
    members_result = await db.exec(
        select(SelectionMember)
        .where(SelectionMember.selection_session_id == session_id)
    )
    members = members_result.all()
    
    return {
        "session": session,
        "access_code": access_code,
        "members": members
    }
