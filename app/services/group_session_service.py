# app/services/group_session_service.py
import random

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.group_session import GroupSession
from app.models.access_code import AccessCode
from app.models.groups import Group
from app.models.field_definition import FieldDefinition
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead, GroupJoinResponse
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
from app.models.preferential_grouping_rule import PreferentialGroupingRule
from app.models.group_member import GroupMember
from typing import Optional, List


async def create_group_session(
    data: GroupSessionCreate,
    host_id: int,
    session: AsyncSession
) -> GroupSessionRead:
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
    # Create the group session
    group_session = GroupSession(
        name=data.name,
        description=data.description,
        code_id=access_code.id,
        host_id=host_id,
        max_group_size=data.max,
        reveal_immediately=data.reveal,
        member_identifier=data.identifier,  # Use code as member identifier
        status="active",
        # Note: The model doesn't have created_at field, we'll add it in the response
    )
    session.add(group_session)
    await session.flush()  # get group_session.id
    # Create the individual named groups
    for group_name in data.group_names:
        group = Group(name=group_name, session_id=group_session.id)
        session.add(group)

    # Create the dynamic fields requested by host
    for field_key in data.fields:
        field_def = FieldDefinition(
            session_id=group_session.id,
            field_key=field_key,
            label=field_key.capitalize(),     # Optional label auto-generated
            data_type="string",               # Default all to string
            required=False,
            options=None
        )
        session.add(field_def)
        
    # Preferential rules handling
    for rule in data.preferential_rules or []:
        rule_model = PreferentialGroupingRule(
            group_session_id=group_session.id,
            field_key=rule.field_key,
            max_per_group=rule.max_per_group
        )
        session.add(rule_model)

    await session.commit()
    await session.refresh(group_session)
    
    # Create a response object that matches the GroupSessionRead schema
    response = GroupSessionRead(
        id=group_session.id,
        name=group_session.name,
        description=group_session.description,
        code_id=access_code.code,  # Map code to code_id as required by schema
        max=group_session.max_group_size,   # Map max_group_size to max
        reveal=group_session.reveal_immediately,  # Map reveal_immediately to reveal
        created_at=datetime.now(timezone.utc),  # Add created_at which is missing
        status=group_session.status
    )
    return response


async def validate_code_and_get_fields(code: str, session: AsyncSession) -> dict:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_code_result = await session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")

    session_result = await session.exec(select(GroupSession).where(GroupSession.code_id == access_code.id))
    group_session = session_result.first()
    if not group_session:
        raise ValueError("Group session not found")

    fields_result = await session.exec(select(FieldDefinition).where(FieldDefinition.session_id == group_session.id))
    field_keys = [field.field_key for field in fields_result.all()]
    
    # Return a dictionary instead of a list
    return {"fields": field_keys, "identifier": group_session.member_identifier}


async def join_group(
    code: str,
    member_identifier: str,
    member_data: dict,
    session: AsyncSession
) -> GroupJoinResponse:
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Validate access code
    access_code_result = await session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")

    # Get group session
    session_result = await session.exec(select(GroupSession).where(GroupSession.code_id == access_code.id))
    group_session = session_result.first()
    if not group_session:
        raise ValueError("Group session not found")

    # Check if member already joined
    dup_check = await session.exec(
        select(GroupMember).where(
            GroupMember.session_id == group_session.id,
            GroupMember.member_identifier == member_identifier
        )
    )
    if dup_check.first():
        raise ValueError("Member already joined")

    # Get all groups for this session
    group_result = await session.exec(select(Group).where(Group.session_id == group_session.id))
    groups = group_result.all()

    # Get all preferential rules for this session
    pref_result = await session.exec(
        select(PreferentialGroupingRule).where(
            PreferentialGroupingRule.group_session_id == group_session.id
        )
    )
    pref_rules = pref_result.all()
    
    # Prepare for group assignment
    eligible_groups = []
    
    # Shuffle the groups for randomization
    shuffled_groups = list(groups)
    random.shuffle(shuffled_groups)
    
    for group in shuffled_groups:
        # Check if group is at maximum capacity
        count_result = await session.exec(
            select(GroupMember).where(GroupMember.group_id == group.id)
        )
        group_members = count_result.all()
        member_count = len(group_members)
        
        if member_count >= group_session.max_group_size:
            continue
        
        # Check all preferential rules
        satisfies_all_rules = True
        
        for rule in pref_rules:
            # Checking if rule applies to the current member
            
            # First, get all the fields defined for this session
            fields_result = await session.exec(select(FieldDefinition).where(FieldDefinition.session_id == group_session.id))
            field_keys = [field.field_key for field in fields_result.all()]
            
            # Check if rule.field_key is one of the defined fields or a specific value
            if rule.field_key in field_keys:
                # Standard field-based rule (e.g., "gender")
                if rule.field_key not in member_data:
                    continue
                    
                member_field_value = str(member_data[rule.field_key])
                
                # Count members in this group with the same field value
                matching_members = 0
                for existing_member in group_members:
                    if rule.field_key in existing_member.member_data:
                        existing_value = str(existing_member.member_data[rule.field_key])
                        if existing_value == member_field_value:
                            matching_members += 1
                
                # Check if adding this member would exceed the limit
                if matching_members >= rule.max_per_group:
                    satisfies_all_rules = False
                    break
            else:
                # Value-based rule (e.g., field_key="female" or "advanced" or any specific value)
                is_match = False
                field_match = None
                
                # Check all fields to see if any matches the rule value
                for field in member_data:
                    if str(member_data[field]).lower() == rule.field_key.lower():
                        is_match = True
                        field_match = field
                        break
                
                if is_match:
                    # Count members in this group with the same value in the matching field
                    matching_members = 0
                    for existing_member in group_members:
                        if field_match in existing_member.member_data:
                            existing_value = str(existing_member.member_data[field_match])
                            if existing_value.lower() == rule.field_key.lower():
                                matching_members += 1
                    
                    # If this member matches and adding them would exceed the limit, mark group as ineligible
                    if matching_members >= rule.max_per_group:
                        satisfies_all_rules = False
                        break
                
        if satisfies_all_rules:
            eligible_groups.append(group)
    
    # If no eligible groups, raise error
    if not eligible_groups:
        raise ValueError("No suitable group available - all groups are either full or would violate preferential grouping rules")
    
    # Randomly select from eligible groups
    selected_group = random.choice(eligible_groups)
    
    # Create the new member
    member = GroupMember(
        group_id=selected_group.id,
        session_id=group_session.id,
        group_name=selected_group.name,
        member_identifier=member_identifier,
        member_data=member_data,
        joined_at=now
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)

    if group_session.reveal_immediately:
        # If reveal is enabled, we can immediately return the response
        return GroupJoinResponse(
            message=f"Successfully joined group {selected_group.name}",
            group_name=selected_group.name,
            session=group_session.name,
            member_identifier=member_identifier
        )
    else:
        return GroupJoinResponse(
            message="Successfully joined a group. Wait for the host to reveal your group.",
            group_name="Hidden",  # Provide a placeholder value
            session=group_session.name,
            member_identifier=member_identifier
        )