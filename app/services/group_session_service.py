# app/services/group_session_service.py

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
