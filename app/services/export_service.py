# app/services/export_service.py
from io import BytesIO
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List, Dict, Any, Tuple
from app.utils.export_logger import log_export

from app.models.group_session import GroupSession
from app.models.selection_session import SelectionSession
from app.models.groups import Group
from app.models.group_member import GroupMember
from app.models.access_code import AccessCode
from app.models.selection_member import SelectionMember

import pandas as pd
import xlsxwriter
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
    db: AsyncSession,
    save_to_disk: bool = False,
    save_directory: str = None
) -> Tuple[BytesIO, Dict[str, Any]]:
    """Generate Excel file for the given session type
    
    Args:
        session_id: ID of the session
        session_type: Type of session ('group' or 'selection')
        db: Database session
        save_to_disk: Whether to save the file to disk (default: False)
        save_directory: Directory to save the file to (required if save_to_disk is True)
        
    Returns:
        Tuple containing the file buffer and metadata dictionary
    """
    # Get session data based on session type
    if session_type == "group":
        session_data = await get_group_session_data(session_id, db)
        
        # Create a workbook and add a worksheet
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        
        # Add session info sheet
        info_sheet = workbook.add_worksheet("Session Info")
        
        # Set up some formatting
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D0D0D0', 'border': 1})
        info_sheet.set_column(0, 0, 30)
        info_sheet.set_column(1, 1, 50)
        
        # Write session details
        row = 0
        info_sheet.write(row, 0, "Session Information", header_format)
        info_sheet.write(row, 1, "", header_format)
        row += 1
        
        info_sheet.write(row, 0, "Name", bold)
        info_sheet.write(row, 1, session_data["session"].name)
        row += 1
        
        info_sheet.write(row, 0, "Description", bold)
        info_sheet.write(row, 1, session_data["session"].description)
        row += 1
        
        info_sheet.write(row, 0, "Access Code", bold)
        info_sheet.write(row, 1, session_data["access_code"].code)
        row += 1
        
        info_sheet.write(row, 0, "Max Group Size", bold)
        info_sheet.write(row, 1, session_data["session"].max_group_size)
        row += 1
        
        info_sheet.write(row, 0, "Status", bold)
        info_sheet.write(row, 1, session_data["session"].status)
        row += 1
        
        info_sheet.write(row, 0, "Generated At", bold)
        info_sheet.write(row, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        row += 2
        
        # Add preferential grouping rules
        if session_data["preferential_rules"]:
            info_sheet.write(row, 0, "Preferential Rules", header_format)
            info_sheet.write(row, 1, "", header_format)
            row += 1
            
            for rule in session_data["preferential_rules"]:
                info_sheet.write(row, 0, f"Field: {rule.field_key}", bold)
                info_sheet.write(row, 1, f"Maximum {rule.max_per_group} per group")
                row += 1
            
            row += 1
        
        # Add field definitions
        if session_data["field_definitions"]:
            info_sheet.write(row, 0, "Field Definitions", header_format)
            info_sheet.write(row, 1, "", header_format)
            row += 1
            
            for field_def in session_data["field_definitions"]:
                info_sheet.write(row, 0, f"Field: {field_def.field_key}", bold)
                
                field_info = f"Label: {field_def.label}, Type: {field_def.data_type}"
                if field_def.options:
                    options_str = ", ".join([f"{k}: {v}" for k, v in field_def.options.items()])
                    field_info += f", Options: {options_str}"
                field_info += f", Required: {'Yes' if field_def.required else 'No'}"
                
                info_sheet.write(row, 1, field_info)
                row += 1
        
        # Add members sheet
        members_sheet = workbook.add_worksheet("Group Members")
        
        # Set column widths
        members_sheet.set_column(0, 0, 20)  # Group Name
        members_sheet.set_column(1, 1, 20)  # Member ID
        members_sheet.set_column(2, 10, 15)  # Fields
        
        # Write headers
        headers = ["Group Name", "Member ID"]
        
        # Get all possible member_data keys (excluding 'name' which is already a column)
        member_data_keys = set()
        for member in session_data["members"]:
            if hasattr(member, 'member_data') and isinstance(member.member_data, dict):
                data_copy = member.member_data.copy()
                if 'name' in data_copy:
                    del data_copy['name']
                member_data_keys.update(data_copy.keys())
        
        # Add member_data fields to headers
        for key in sorted(list(member_data_keys)):
            headers.append(f"Field: {key}")
        
        for col, header in enumerate(headers):
            members_sheet.write(0, col, header, bold)
        
        # Get a reference to member_data_keys that we created above
        sorted_member_data_keys = sorted(list(member_data_keys))
        
        # Write member data
        row = 1
        for group in session_data["groups"]:
            group_members = [m for m in session_data["members"] if m.group_id == group.id]
            for member in group_members:
                col = 0
                members_sheet.write(row, col, group.name)
                col += 1
                members_sheet.write(row, col, member.member_identifier)
                col += 1
                
                # Write additional member data fields
                if hasattr(member, 'member_data') and isinstance(member.member_data, dict):
                    data_copy = member.member_data.copy()
                    if 'name' in data_copy:  # Skip name as it's already in column 1
                        del data_copy['name']
                    
                    # Add each member_data field in the same order as the headers
                    for i, key in enumerate(sorted_member_data_keys):
                        if key in data_copy:
                            members_sheet.write(row, col + i, str(data_copy[key]))
                        else:
                            members_sheet.write(row, col + i, "")
                
                row += 1
        
        # Close the workbook
        workbook.close()
        
        # Save to disk if requested
        if save_to_disk and save_directory:
            import os
            from pathlib import Path
            
            # Create directory if it doesn't exist
            Path(save_directory).mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = f"{session_type}_session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(save_directory, filename)
            
            # Save a copy to disk
            buffer.seek(0)
            with open(filepath, 'wb') as file:
                file.write(buffer.getvalue())
            
            print(f"Excel file saved to: {filepath}")
        
        # Reset buffer position for streaming
        buffer.seek(0)
        
        # Return the file buffer and session metadata
        return buffer, {
            "session_name": session_data["session"].name,
            "session_description": session_data["session"].description
        }
        
    elif session_type == "selection":
        session_data = await get_selection_session_data(session_id, db)
        
        # Create a workbook and add a worksheet
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        
        # Add session info sheet
        info_sheet = workbook.add_worksheet("Session Info")
        
        # Set up some formatting
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D0D0D0', 'border': 1})
        info_sheet.set_column(0, 0, 30)
        info_sheet.set_column(1, 1, 50)
        
        # Write session details
        row = 0
        info_sheet.write(row, 0, "Session Information", header_format)
        info_sheet.write(row, 1, "", header_format)
        row += 1
        
        info_sheet.write(row, 0, "Name", bold)
        info_sheet.write(row, 1, session_data["session"].name)
        row += 1
        
        info_sheet.write(row, 0, "Description", bold)
        info_sheet.write(row, 1, session_data["session"].description or "N/A")
        row += 1
        
        info_sheet.write(row, 0, "Access Code", bold)
        info_sheet.write(row, 1, session_data["access_code"].code)
        row += 1
        
        info_sheet.write(row, 0, "Max Group Size", bold)
        info_sheet.write(row, 1, session_data["session"].max_group_size)
        row += 1
        
        info_sheet.write(row, 0, "Generated At", bold)
        info_sheet.write(row, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        row += 2
        
        # Add preferential selection rules
        if session_data["preferential_rules"]:
            info_sheet.write(row, 0, "Preferential Rules", header_format)
            info_sheet.write(row, 1, "", header_format)
            row += 1
            
            for rule in session_data["preferential_rules"]:
                info_sheet.write(row, 0, f"Field: {rule.field_key}", bold)
                info_sheet.write(row, 1, f"Maximum selection: {rule.preference_max_selection}")
                row += 1
        
        # Sort members - selected members first
        sorted_members = sorted(session_data["members"], key=lambda m: not m.selected)
        
        # Add members sheet
        members_sheet = workbook.add_worksheet("Selection Members")
        
        # Set column widths
        members_sheet.set_column(0, 0, 20)  # Member ID
        members_sheet.set_column(1, 1, 10)  # Selected
        members_sheet.set_column(2, 2, 20)  # Joined At
        members_sheet.set_column(3, 15, 15)  # Attributes
        
        # Create formats
        bold = workbook.add_format({'bold': True})
        selected_format = workbook.add_format({'bg_color': '#E0EFE0'})  # Light green
        
        # Add summary at top
        selected_count = sum(1 for m in session_data["members"] if m.selected)
        total_count = len(session_data["members"])
        members_sheet.write(0, 0, "Selection Summary:", bold)
        members_sheet.write(0, 1, f"{selected_count} selected out of {total_count} total members")
        
        # Get all possible attribute keys
        attribute_keys = set()
        for member in session_data["members"]:
            if member.attributes and isinstance(member.attributes, dict):
                attribute_keys.update(member.attributes.keys())
        
        attribute_keys = sorted(list(attribute_keys))
        
        # Write headers
        headers = ["Member ID", "Selected", "Joined At"] + attribute_keys
        for col, header in enumerate(headers):
            members_sheet.write(2, col, header, bold)
        
        # Write member data
        for i, member in enumerate(sorted_members):
            row = i + 3  # Start at row 3 (after summary and headers)
            
            # Apply formatting if selected
            row_format = selected_format if member.selected else None
            
            # Write member basic data
            members_sheet.write(row, 0, member.member_identifier, row_format)
            members_sheet.write(row, 1, "Yes" if member.selected else "No", row_format)
            joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A"
            members_sheet.write(row, 2, joined_at, row_format)
            
            # Write attributes
            if member.attributes and isinstance(member.attributes, dict):
                for j, key in enumerate(attribute_keys):
                    if key in member.attributes:
                        value = member.attributes[key]
                        members_sheet.write(row, j + 3, str(value), row_format)
        
        # Close the workbook
        workbook.close()
        
        # Save to disk if requested
        if save_to_disk and save_directory:
            import os
            from pathlib import Path
            
            # Create directory if it doesn't exist
            Path(save_directory).mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = f"{session_type}_session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(save_directory, filename)
            
            # Save a copy to disk
            buffer.seek(0)
            with open(filepath, 'wb') as file:
                file.write(buffer.getvalue())
            
            print(f"Excel file saved to: {filepath}")
        
        # Reset buffer position for streaming
        buffer.seek(0)
        
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
    db: AsyncSession,
    save_to_disk: bool = False,
    save_directory: str = None
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
        
        # Preferential Rules
        if session_data["preferential_rules"]:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Preferential Rules", ln=True)
            
            pdf.set_font("Arial", "", 12)
            for rule in session_data["preferential_rules"]:
                pdf.cell(0, 10, f"Field: {rule.field_key} - Maximum {rule.max_per_group} per group", ln=True)
        
        # Field Definitions
        if session_data["field_definitions"]:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Field Definitions", ln=True)
            
            pdf.set_font("Arial", "", 12)
            for field_def in session_data["field_definitions"]:
                field_info = f"Field: {field_def.field_key} - Label: {field_def.label}, Type: {field_def.data_type}"
                pdf.cell(0, 10, field_info, ln=True)
                
                if field_def.options:
                    options_str = ", ".join([f"{k}: {v}" for k, v in field_def.options.items()])
                    pdf.cell(0, 10, f"    Options: {options_str}", ln=True)
                
                pdf.cell(0, 10, f"    Required: {'Yes' if field_def.required else 'No'}", ln=True)
        
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
            pdf.cell(50, 10, "Member ID", border=1)
            pdf.cell(140, 10, "Member Data", border=1)
            pdf.ln()
            
            # List members in this group
            pdf.set_font("Arial", "", 11)
            for member in [m for m in session_data["members"] if m.group_id == group.id]:
                pdf.cell(50, 10, member.member_identifier, border=1)
                
                # Format member_data as a string
                member_data_str = "N/A"
                if hasattr(member, 'member_data') and isinstance(member.member_data, dict):
                    data_copy = member.member_data.copy()
                    
                    if data_copy:
                        member_data_str = ", ".join([f"{k}: {v}" for k, v in data_copy.items()])
                
                # Handle long data strings with multi_cell for text wrapping
                current_x = pdf.get_x()
                current_y = pdf.get_y()
                
                # Calculate if text will fit in one line
                if pdf.get_string_width(member_data_str) > 140:
                    # Use multi_cell for text wrapping
                    pdf.multi_cell(140, 10, member_data_str, border=1)
                else:
                    # Use regular cell for single line
                    pdf.cell(140, 10, member_data_str, border=1)
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
        
        # Preferential Selection Rules
        if session_data["preferential_rules"]:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Preferential Selection Rules", ln=True)
            
            pdf.set_font("Arial", "", 12)
            for rule in session_data["preferential_rules"]:
                pdf.cell(0, 10, f"Field: {rule.field_key} - Preference Maximum: {rule.preference_max_selection}", ln=True)
        
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
        
        # Sort members - selected members first
        sorted_members = sorted(session_data["members"], key=lambda m: not m.selected)
        
        # Get count of selected members
        selected_count = sum(1 for m in session_data["members"] if m.selected)
        total_count = len(session_data["members"])
        
        # Add selection summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Selection Summary: {selected_count} selected out of {total_count} total members", ln=True)
        pdf.ln(5)
        
        # List all members (selected first)
        pdf.set_font("Arial", "", 11)
        for member in sorted_members:
            # Highlight selected members with light gray background
            if member.selected:
                pdf.set_fill_color(230, 230, 230)  # Light gray
                fill = True
            else:
                fill = False
                
            pdf.cell(40, 10, member.member_identifier, border=1, fill=fill)
            pdf.cell(30, 10, "Yes" if member.selected else "No", border=1, fill=fill)
            pdf.cell(60, 10, member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A", border=1, fill=fill)
            
            # Format attributes as string
            attr_str = "N/A"
            if member.attributes and isinstance(member.attributes, dict):
                attr_str = ", ".join([f"{k}: {v}" for k, v in member.attributes.items()])
                
            # Handle long attribute strings with multi_cell for text wrapping
            if pdf.get_string_width(attr_str) > 60:
                current_x = pdf.get_x()
                current_y = pdf.get_y()
                
                # Use multi_cell for text wrapping
                pdf.multi_cell(60, 10, attr_str, border=1, fill=fill)
            else:
                # Use regular cell for single line
                pdf.cell(60, 10, attr_str, border=1, fill=fill)
                pdf.ln()
    
    else:
        raise ValueError(f"Unknown session type: {session_type}")
        
    # Save PDF to buffer
    pdf_data = pdf.output(dest='S')
    # Handle different return types from fpdf.output
    if isinstance(pdf_data, str):
        buffer.write(pdf_data.encode('latin-1'))
    elif isinstance(pdf_data, bytes) or isinstance(pdf_data, bytearray):
        buffer.write(pdf_data)
    buffer.seek(0)
    
    # Save to disk if requested
    if save_to_disk and save_directory:
        import os
        from pathlib import Path
        
        # Create directory if it doesn't exist
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{session_type}_session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(save_directory, filename)
        
        # Save file
        with open(filepath, 'wb') as file:
            # Need to create a copy of the buffer since we already used seek(0)
            buffer_copy = BytesIO(buffer.getvalue())
            file.write(buffer_copy.getvalue())
        
        print(f"PDF saved to: {filepath}")
    
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
    
    # Get preferential grouping rules
    from app.models.preferential_grouping_rule import PreferentialGroupingRule
    rules_result = await db.exec(
        select(PreferentialGroupingRule)
        .where(PreferentialGroupingRule.group_session_id == session_id)
    )
    preferential_rules = rules_result.all()
    
    # Get field definitions
    from app.models.field_definition import FieldDefinition
    field_defs_result = await db.exec(
        select(FieldDefinition)
        .where(FieldDefinition.session_id == session_id)
    )
    field_definitions = field_defs_result.all()
    
    return {
        "session": session,
        "access_code": access_code,
        "groups": groups,
        "members": members,
        "preferential_rules": preferential_rules,
        "field_definitions": field_definitions
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
    
    # Get preferential selection rules
    from app.models.preferential_selection_rule import PreferentialSelectionRule
    rules_result = await db.exec(
        select(PreferentialSelectionRule)
        .where(PreferentialSelectionRule.selection_session_id == session_id)
    )
    preferential_rules = rules_result.all()
    
    return {
        "session": session,
        "access_code": access_code,
        "members": members,
        "preferential_rules": preferential_rules
    }
