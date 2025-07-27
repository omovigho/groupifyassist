# app/services/group_session_service.py
import random

from groupifyassist.app.schemas.selection_session import SelectionSessionCreate, SelectionSessionRead
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.group_session import GroupSession
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode
from app.models.groups import Group
from app.models.field_definition import FieldDefinition
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead, GroupJoinResponse
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
from app.models.preferential_grouping_rule import PreferentialGroupingRule
from app.models.group_member import GroupMember
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
        title=data.title,
        description=data.description,
        code_id=access_code.id,
        host_id=host_id,
        max_group_size=data.max,
        member_identifier=data.identifier,  # Use code as member identifier
        status="active",
        # Note: The model doesn't have created_at field, we'll add it in the response
    )
    session.add(selection_session)
    await session.flush()  # get selection_session.id
    # Create the individual named groups
    for group_name in data.group_names:
        group = Group(name=group_name, session_id=selection_session.id)
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