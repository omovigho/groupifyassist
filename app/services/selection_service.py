# app/services/group_session_service.py
import random

from app.schemas.selection_session import SelectionSessionCreate, SelectionSessionRead, SelectionJoinResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode
from app.models.selection_member import SelectionMember
from app.models.field_definition import FieldDefinition
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
from app.models.preferential_selection_rule import PreferentialSelectionRule
from typing import Optional, List


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

    # Create the dynamic fields requested by host
    for field_key in data.fields:
        field_def = FieldDefinition(
            session_id=selection_session.id,
            field_key=field_key,
            label=field_key.capitalize(),     # Optional label auto-generated
            data_type="string",               # Default all to string
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

    fields_result = await session.exec(select(FieldDefinition).where(FieldDefinition.session_id == selection_session.id))
    field_keys = [field.field_key for field in fields_result.all()]
    
    # Return a dictionary instead of a list
    return {"fields": field_keys, "identifier": selection_session.member_identifier}


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