from typing import Optional
from sqlmodel import SQLModel, Field


class Group(SQLModel, table=True):
    __tablename__ = "groups"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g. "Group A"
    session_id: int = Field(foreign_key="group_sessions.id")  # Links to GroupSession
