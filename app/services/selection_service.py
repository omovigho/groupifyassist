# app/services/selection_service.py
import random
from functools import lru_cache

from app.schemas.selection_session import SelectionSessionCreate, SelectionSessionRead, SelectionJoinResponse
from app.schemas.selection import SelectMembersRequest, SelectionResult, MemberSelectionDetail
from sqlmodel import select, and_, not_, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode
from app.models.selection_member import SelectionMember
from app.models.selection_log import SelectionLog
from app.models.field_definition import FieldDefinition
from app.models.selection_field_definition import SelectionFieldDefinition
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
from app.models.preferential_selection_rule import PreferentialSelectionRule
from typing import Optional, List, Dict, Tuple, Set


async def create_selection_session(
    data: SelectionSessionCreate,
    host_id: int,
    session: AsyncSession
) -> SelectionSessionRead:
    # Generate a unique join code
    code = generate_group_code()

    # Check if code already exists (loop until unique)
    while True:
        result = await session.exec(select(AccessCode).where((AccessCode.code == code) & (AccessCode.status == "active")))
        if not result.first():
            break
        code = generate_group_code()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = now + timedelta(minutes=data.expires_in or 1440)

    # Create access code entry
    access_code = AccessCode(
        code=code,
        status="active",
        host_id=host_id,
        created_at=now,
        expires_at=expires_at
    )
    session.add(access_code)
    await session.flush()  # get access_code.id
    # Create the selection session
    selection_session = SelectionSession(
        name=data.name,
        description=data.description,
        max_group_size=data.max,
        code_id=access_code.id,
        host_id=host_id,
        member_identifier=data.identifier,  # Use code as member identifier
    )
    session.add(selection_session)
    await session.flush()  # get selection_session.id

    # Create the dynamic fields requested by host (separate table for selections)
    for field_key in data.fields:
        field_def = SelectionFieldDefinition(
            selection_session_id=selection_session.id,
            field_key=field_key,
            label=field_key.capitalize(),     # Optional label auto-generated
            data_type="string",              # Default all to string
            required=False,
            options=None
        )
        session.add(field_def)
        
    # Preferential rules handling
    for rule in data.preferential_rules or []:
        rule_model = PreferentialSelectionRule(
            selection_session_id=selection_session.id,
            field_key=rule.field_key,
            preference_max_selection=rule.preference_max_selection
        )
        session.add(rule_model)

    await session.commit()
    await session.refresh(selection_session)
    
    # Create a response object that matches the SelectionSessionRead schema
    response = SelectionSessionRead(
        id=selection_session.id,
        name=selection_session.name,
        description=selection_session.description,
        max=selection_session.max_group_size,
        code_id=access_code.code,  # Map code to code_id as required by schema
        created_at=datetime.now(timezone.utc),  # Add created_at which is missing
    )
    return response


async def validate_code_and_get_fields(code: str, session: AsyncSession) -> dict:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_code_result = await session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")

    session_result = await session.exec(select(SelectionSession).where(SelectionSession.code_id == access_code.id))
    selection_session = session_result.first()
    if not selection_session:
        raise ValueError("Selection session not found")

    # Fetch fields from selection-specific table; fallback to legacy shared table if needed
    fields_result = await session.exec(
        select(SelectionFieldDefinition).where(SelectionFieldDefinition.selection_session_id == selection_session.id)
    )
    s_fields = fields_result.all()
    field_keys = [field.field_key for field in s_fields]
    if not field_keys:
        legacy_result = await session.exec(select(FieldDefinition).where(FieldDefinition.session_id == selection_session.id))
        field_keys = [f.field_key for f in legacy_result.all()]
    
    # Return enriched metadata for UI
    return {
        "name": selection_session.name,
        "description": selection_session.description,
        "fields": field_keys,
        "identifier": selection_session.member_identifier,
    }


async def join_group(
    code: str,
    member_identifier: str,
    member_data: dict,
    session: AsyncSession
) -> SelectionJoinResponse:
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Validate access code
    access_code_result = await session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")

    # Get selection session
    selection_query = await session.exec(select(SelectionSession).where(SelectionSession.code_id == access_code.id))
    selection_session = selection_query.first()
    if not selection_session:
        raise ValueError("Selection session not found")

    # Check if member already joined
    dup_check = await session.exec(
        select(SelectionMember).where(
            SelectionMember.selection_session_id == selection_session.id,
            SelectionMember.member_identifier == member_identifier
        )
    )
    if dup_check.first():
        raise ValueError("Member already joined")

    # Count total members for this session
    count_result = await session.exec(
        select(SelectionMember).where(
            SelectionMember.selection_session_id == selection_session.id
        )
    )
    member_count = len(count_result.all())
    
    # Check if selection session is at maximum capacity
    if member_count >= selection_session.max_group_size:
        raise ValueError("Selection session has reached maximum capacity")
    
    # Get all preferential rules for this session
    pref_result = await session.exec(
        select(PreferentialSelectionRule).where(
            PreferentialSelectionRule.selection_session_id == selection_session.id
        )
    )
    pref_rules = pref_result.all()
    
    # Check all preferential rules to see if joining would violate any rules
    for rule in pref_rules:
        # Check if the rule applies to this member
        if rule.field_key in member_data:
            member_field_value = str(member_data[rule.field_key])
            
            # Count members with the same field value already selected
            selected_count = await session.exec(
                select(SelectionMember).where(
                    SelectionMember.selection_session_id == selection_session.id,
                    SelectionMember.selected == True
                )
            )
            selected_members = selected_count.all()
            
            matching_selected = 0
            for existing_member in selected_members:
                if rule.field_key in existing_member.attributes:
                    if str(existing_member.attributes[rule.field_key]) == member_field_value:
                        matching_selected += 1
            
            # Check if adding this member would exceed the preferential limit
            if matching_selected >= rule.preference_max_selection:
                # The rule is violated, but we don't reject the member - they just won't be selected
                # The member can still join but might not be selected based on this rule
                pass
    
    # Create the new selection member
    selection_member = SelectionMember(
        selection_session_id=selection_session.id,
        member_identifier=member_identifier,
        attributes=member_data,
        selected=False,
        joined_at=now
    )
    
    session.add(selection_member)
    await session.commit()
    await session.refresh(selection_member)

    # Return successful join response
    return SelectionJoinResponse(
        message="Successfully joined the selection session.",
        session=selection_session.name,
        member_identifier=member_identifier
    )


async def select_members(
    data: SelectMembersRequest,
    host_id: int,  # Add host_id parameter to verify ownership
    db_session: AsyncSession
) -> SelectionResult:
    """
    Select members from a session based on count and preferential selection criteria.
    
    Args:
        data: Contains code, count, and optional preferential_selection
        host_id: ID of the host making the request (for ownership verification)
        db_session: Database session
    
    Returns:
        SelectionResult with details of the selection
    """
    # Validate access code and get the selection session
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_code_result = await db_session.exec(select(AccessCode).where(AccessCode.code == data.code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")
    
    # Verify the host is the owner of this code
    if access_code.host_id != host_id:
        raise ValueError("You are not authorized to select members for this session")
    
    # Get the selection session
    session_result = await db_session.exec(
        select(SelectionSession).where(SelectionSession.code_id == access_code.id)
    )
    selection_session = session_result.first()
    if not selection_session:
        raise ValueError("Selection session not found")
    
    # Get all members that have already been selected
    selected_members_query = await db_session.exec(
        select(SelectionMember).where(
            SelectionMember.selection_session_id == selection_session.id,
            SelectionMember.selected == True
        )
    )
    already_selected_members = selected_members_query.all()
    already_selected_ids = {member.id for member in already_selected_members}
    
    # If we have more selected members than requested, raise an error
    if len(already_selected_members) >= data.count:
        raise ValueError(f"Already selected {len(already_selected_members)} members, which is equal to or more than requested count of {data.count}")
    
    # Number of members we still need to select
    remaining_to_select = data.count - len(already_selected_members)
    
    # Track selection details for preferential and random selections
    preferential_selected = []
    random_selected = []
    
    # Get all members in the session who have not been selected yet
    unselected_members_query = await db_session.exec(
        select(SelectionMember).where(
            SelectionMember.selection_session_id == selection_session.id,
            SelectionMember.selected == False
        )
    )
    unselected_members = unselected_members_query.all()
    
    # If we have preferential selection criteria, prioritize those members
    if data.preferential_selection and remaining_to_select > 0:
        field_key = list(data.preferential_selection.keys())[0]  # Get the field key
        field_value = data.preferential_selection[field_key]  # Get the field value
        
        # Get all preferential rules for this session
        pref_rule_query = await db_session.exec(
            select(PreferentialSelectionRule).where(
                PreferentialSelectionRule.selection_session_id == selection_session.id
            )
        )
        pref_rules = pref_rule_query.all()
        
        # Determine max number for this preference
        preferential_max = remaining_to_select  # Default to all remaining
        
        # Handle two types of rules:
        # 1. Rules where field_key is an actual field (like "gender") - match by field and value
        # 2. Rules where field_key is a specific value (like "female") - direct match
        for rule in pref_rules:
            
            # Direct match with the value (e.g., rule.field_key = "female")
            if rule.field_key.lower() == field_value.lower():
                print(f"Value match found! Setting max to: {rule.preference_max_selection}")
                preferential_max = min(preferential_max, rule.preference_max_selection)
        
        # Count how many of this preference are already selected
        already_preferential_count = 0
        for member in already_selected_members:
            # For field:value pair match (e.g., gender=female)
            if field_key in member.attributes and str(member.attributes[field_key]).lower() == field_value.lower():
                already_preferential_count += 1
        
        # Adjust max based on already selected members with this preference
        if already_preferential_count >= preferential_max:
            preferential_max = 0  # Already reached the limit
        else:
            preferential_max -= already_preferential_count
            
        # Find members that match the preferential criteria
        preferential_members = []
        for member in unselected_members:
            if field_key in member.attributes and str(member.attributes[field_key]).lower() == field_value.lower():
                preferential_members.append(member)
        
        # Randomly shuffle the preferential members for fair selection
        random.shuffle(preferential_members)
        
        # Select up to preferential_max members (respecting the preference limit)
        # or remaining_to_select, whichever is smaller
        max_to_select = min(preferential_max, remaining_to_select)
        
        preferential_selected = preferential_members[:max_to_select]
        remaining_to_select -= len(preferential_selected)
    
    # If we still need more members, select them randomly
    if remaining_to_select > 0:
        # Get the remaining unselected members who were not selected in the preferential round
        remaining_unselected = [m for m in unselected_members if m not in preferential_selected]
        
        # For members selected by preference with gender=female, we need to avoid selecting more females
        # if we have a rule limiting females
        if data.preferential_selection:
            field_key = list(data.preferential_selection.keys())[0]
            field_value = data.preferential_selection[field_key]
            
            # Check if there's a rule for this specific value
            rule_for_value = False
            max_allowed = None
            for rule in pref_rules:
                if rule.field_key.lower() == field_value.lower():
                    rule_for_value = True
                    max_allowed = rule.preference_max_selection
                    break
                    
            if rule_for_value:
                # Count total selected including already selected and newly preferential selected
                current_count = already_preferential_count + len(preferential_selected)
                
                # If we're already at or over the limit, exclude members with this value from random selection
                if current_count >= max_allowed:
                    remaining_unselected = [m for m in remaining_unselected if not (
                        field_key in m.attributes and str(m.attributes[field_key]).lower() == field_value.lower()
                    )]
        
        # Randomly shuffle the remaining unselected members
        random.shuffle(remaining_unselected)
        
        # Select up to remaining_to_select random members
        random_selected = remaining_unselected[:remaining_to_select]
    
    # Combine all selected members
    newly_selected_members = preferential_selected + random_selected
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Create SelectionLog entries and update member selection status
    for member in newly_selected_members:
        # Determine selection type
        selection_type = "preferential" if member in preferential_selected else "random"
        
        # Create log entry
        selection_log = SelectionLog(
            selection_session_id=selection_session.id,
            member_id=member.id,
            selected_at=now,
            selection_type=selection_type
        )
        db_session.add(selection_log)
        
        # Update member status to selected
        member.selected = True
        db_session.add(member)
    
    # Commit the changes
    await db_session.commit()
    
    # Create response with details
    selected_member_identifiers = [m.member_identifier for m in already_selected_members] + [m.member_identifier for m in newly_selected_members]
    
    # For debugging, count how many of the selected members match the preferential criteria
    if data.preferential_selection:
        field_key = list(data.preferential_selection.keys())[0]
        field_value = data.preferential_selection[field_key]
        
        # Count in all selected members (already selected + newly selected)
        all_selected = already_selected_members + newly_selected_members
        matching_count = 0
        
        for member in all_selected:
            if field_key in member.attributes and str(member.attributes[field_key]).lower() == field_value.lower():
                matching_count += 1

        
        # Check against rule limits
        for rule in pref_rules:
            if rule.field_key.lower() == field_value.lower():
                if matching_count > rule.preference_max_selection:
                    print("WARNING: Selected more than the rule limit!")

    # Create the result object
    result = SelectionResult(
        selected_count=len(already_selected_members) + len(newly_selected_members),
        preferential_count=len(preferential_selected),
        random_count=len(random_selected) + len(already_selected_members),
        member_identifiers=selected_member_identifiers
    )
    
    return result


async def get_selected_members(
    code: str,
    host_id: int,  # Add host_id parameter to verify ownership
    db_session: AsyncSession
) -> List[MemberSelectionDetail]:
    """
    Get details of all selected members in a session.
    
    Args:
        code: The session access code
        host_id: ID of the host making the request (for ownership verification)
        db_session: Database session
    
    Returns:
        List of MemberSelectionDetail with selected member information
    """
    # Validate access code and get the selection session
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_code_result = await db_session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")
    
    # Verify the host is the owner of this code
    if access_code.host_id != host_id:
        raise ValueError("You are not authorized to view members for this session")
    
    # Get the selection session
    session_result = await db_session.exec(
        select(SelectionSession).where(SelectionSession.code_id == access_code.id)
    )
    selection_session = session_result.first()
    if not selection_session:
        raise ValueError("Selection session not found")
    
    # Get all selected members and their selection logs
    query = select(SelectionMember, SelectionLog).where(
        SelectionMember.selection_session_id == selection_session.id,
        SelectionMember.selected == True,
        SelectionLog.member_id == SelectionMember.id
    )
    
    result = await db_session.exec(query)
    member_logs = result.all()
    
    # Transform the result into the response format
    selected_members = []
    for member, log in member_logs:
        selected_members.append(MemberSelectionDetail(
            id=member.id,
            member_identifier=member.member_identifier,
            attributes=member.attributes,
            selection_type=log.selection_type,
            selected_at=log.selected_at
        ))
    
    return selected_members


async def clear_selections(
    code: str,
    host_id: int,  # Add host_id parameter to verify ownership
    db_session: AsyncSession
) -> int:
    """
    Clear all selections for a session, resetting members' selected status.
    
    Args:
        code: The session access code
        host_id: ID of the host making the request (for ownership verification)
        db_session: Database session
    
    Returns:
        Number of members whose selection was cleared
    """
    # Validate access code and get the selection session
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_code_result = await db_session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")
    
    # Verify the host is the owner of this code
    if access_code.host_id != host_id:
        raise ValueError("You are not authorized to clear selections for this session")
    
    # Get the selection session
    session_result = await db_session.exec(
        select(SelectionSession).where(SelectionSession.code_id == access_code.id)
    )
    selection_session = session_result.first()
    if not selection_session:
        raise ValueError("Selection session not found")
    
    # Get all selected members
    selected_members_query = await db_session.exec(
        select(SelectionMember).where(
            SelectionMember.selection_session_id == selection_session.id,
            SelectionMember.selected == True
        )
    )
    selected_members = selected_members_query.all()
    
    # Update selected status to False
    for member in selected_members:
        member.selected = False
        db_session.add(member)
    
    # Remove selection logs
    logs_query = await db_session.exec(
        select(SelectionLog).where(
            SelectionLog.selection_session_id == selection_session.id
        )
    )
    logs = logs_query.all()
    
    # Delete logs
    for log in logs:
        await db_session.delete(log)
    
    # Commit the changes
    await db_session.commit()
    
    # Return the number of cleared selections
    return len(selected_members)