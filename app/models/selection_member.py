from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from datetime import datetime

class SelectionMember(SQLModel, table=True):
    __tablename__ = "selection_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    selection_session_id: int = Field(foreign_key="selection_sessions.id")
    attributes: dict = Field(sa_column=Column(JSONB))
    #attributes: dict = Field(sa_column_kwargs={"type_": JSONB})  # dynamic info
    member_identifier: str  # unique within the selection session
    selected: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.now)
