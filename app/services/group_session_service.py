'''# app/services/group_session_service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.group_session import GroupSession
from app.models.access_code import AccessCode
from app.schemas.group_session import GroupSessionCreate, GroupSessionRead
from app.utils.code_generator import generate_group_code
from datetime import datetime, timedelta, timezone
from typing import Optional


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
from typing import Optional


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
        access_code_id=access_code.id,
        host_id=host_id,
        max_group_size=data.max,
        reveal_immediately=data.reveal,
        status="active",
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
    return group_session


# Sample JSON payload to test:
'''
POST /groups/create
Authorization: Bearer <your_token>

{
  "name": "Orientation Grouping",
  "title": "Freshers Welcome",
  "description": "Divide new students into discussion groups",
  "max": 6,
  "reveal": true,
  "expires_in": 180,
  "group_names": ["Group A", "Group B", "Group C"],
  "fields": [
    {"field_key": "fullname", "label": "Full Name", "data_type": "string"},
    {"field_key": "gender", "label": "Gender", "data_type": "enum", "options": {"values": ["male", "female"]}},
    {"field_key": "age", "label": "Age", "data_type": "number"},
    {"field_key": "department", "label": "Department", "data_type": "string"}
  ]
}
'''

# Make sure your models include:
# - `Group` model with name, session_id
# - `FieldDefinition` model with field_key, label, data_type, etc.
# - `GroupSession` model using access_code_id not code
