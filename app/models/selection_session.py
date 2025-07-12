from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class SelectionSession(SQLModel, table=True):
    __tablename__ = "selection_sessions"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    code: str = Field(index=True, unique=True)
    host_id: int = Field(foreign_key="users.id")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
