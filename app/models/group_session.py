from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class GroupSession(SQLModel, table=True):
    __tablename__ = "group_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    title: str
    description: str
    code: str = Field(index=True, unique=True)
    host_id: int = Field(foreign_key="users.id")
    max_group_size: int
    reveal_immediately: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
