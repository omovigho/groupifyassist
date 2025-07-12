from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from datetime import datetime

class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    group_session_id: int = Field(foreign_key="group_sessions.id")
    group_name: str  # e.g. "Team A", "Group 1"
    attributes: dict = Field(sa_column=Column(JSONB))
    #attributes: dict = Field(sa_column_kwargs={"type_": JSONB})  # dynamic member info
    member_identifier: str  # unique ID within the session
    joined_at: datetime = Field(default_factory=datetime.now)
