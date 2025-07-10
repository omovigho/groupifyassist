from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class SelectionLog(SQLModel, table=True):
    __tablename__ = "selection_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    selection_session_id: int = Field(foreign_key="selection_sessions.id")
    member_id: int = Field(foreign_key="selection_members.id")
    selected_at: datetime = Field(default_factory=datetime.now)
    selection_type: str = Field(default="random")  # or 'preferential'
