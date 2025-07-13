from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class AccessCode(SQLModel, table=True):
    __tablename__ = "access_codes"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str #= Field(index=True, unique=True)
    host_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: str = Field(default="active")  # values: active, used, expired
