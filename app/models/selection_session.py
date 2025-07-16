from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class SelectionSession(SQLModel, table=True):
    __tablename__ = "selection_sessions"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    code_id: int = Field(foreign_key="access_codes.id")
    host_id: int = Field(foreign_key="users.id")