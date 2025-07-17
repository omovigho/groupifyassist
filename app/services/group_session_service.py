'''# app/services/group_session_service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.group_session import GroupSession
from app.models.access_code import AccessCode
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
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

    # Create group session
    group_session = GroupSession(
        name=data.name,
        code=code,
        host_id=host_id,
        max=data.max,
        reveal=data.reveal,
        created_at=datetime.now(timezone.utc),
        expired=False
    )
    session.add(group_session)
    await session.flush()  # to get group_session.id before committing

    # Set expiration (default 24 hours or custom duration)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=data.expires_in or 1440)

    # Create corresponding access code
    access_code = AccessCode(
        code=code,
        status="active",
        host_id=host_id,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at
    )
    session.add(access_code)
    await session.commit()
    await session.refresh(group_session)

    return group_session


'''
# app/services/group_session_service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.group_session import GroupSession
from app.models.access_code import AccessCode
from app.models.groups import Group
from app.models.field_definition import FieldDefinition
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead
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
    return {"fields": field_keys}


async def join_group(
    code: str,
    member_identifier: str,
    member_data: dict,
    session: AsyncSession
) -> GroupMember:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    access_code_result = await session.exec(select(AccessCode).where(AccessCode.code == code))
    access_code = access_code_result.first()
    if not access_code or access_code.expires_at < now or access_code.status != "active":
        raise ValueError("Invalid or expired code")

    session_result = await session.exec(select(GroupSession).where(GroupSession.code_id == access_code.id))
    group_session = session_result.first()
    if not group_session:
        raise ValueError("Group session not found")

    dup_check = await session.exec(
        select(GroupMember).where(
            GroupMember.session_id == group_session.id,
            GroupMember.member_identifier == member_identifier
        )
    )
    if dup_check.first():
        raise ValueError("Member already joined")

    group_result = await session.exec(select(Group).where(Group.session_id == group_session.id))
    groups = group_result.all()

    group_counts = {}
    for group in groups:
        count_result = await session.exec(
            select(GroupMember).where(GroupMember.group_id == group.id)
        )
        group_counts[group.id] = len(count_result.all())

    pref_result = await session.exec(
        select(PreferentialGroupingRule).where(
            PreferentialGroupingRule.group_session_id == group_session.id
        )
    )
    pref_rules = pref_result.all()

    selected_group = None
    for group in groups:
        if group_counts[group.id] >= group_session.max_group_size:
            continue

        satisfies_all = True
        for rule in pref_rules:
            if rule.field_key in member_data:
                rule_count_result = await session.exec(
                    select(GroupMember).where(
                        GroupMember.group_id == group.id,
                        GroupMember.member_data[rule.field_key].astext == member_data[rule.field_key]
                    )
                )
                count = len(rule_count_result.all())
                if count >= rule.max_per_group:
                    satisfies_all = False
                    break

        if satisfies_all:
            selected_group = group
            break

    if not selected_group:
        raise ValueError("No suitable group available for this member")

    member = GroupMember(
        group_id=selected_group.id,
        session_id=group_session.id,
        member_identifier=member_identifier,
        member_data=member_data,
        joined_at=now
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)

    return member
