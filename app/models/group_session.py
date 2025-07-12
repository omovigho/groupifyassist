from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class GroupSession(SQLModel, table=True):
    __tablename__ = "group_sessions"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    title: str
    description: str
    code: str = Field(index=True, unique=True)
    host_id: int = Field(foreign_key="users.id")
    max_group_size: int
    reveal_immediately: bool = Field(default=False)
    
    status: str = Field(default="active")  # values: active, used, expired
