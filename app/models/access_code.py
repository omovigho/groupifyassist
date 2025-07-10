from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class AccessCode(SQLModel, table=True):
    __tablename__ = "access_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    host_id: int = Field(foreign_key="users.id")
    status: str = Field(default="active")  # values: active, used, expired
