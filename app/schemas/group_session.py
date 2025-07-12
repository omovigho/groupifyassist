# app/schemas/group_session.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GroupSessionCreate(BaseModel):
    name: str
    max: int
    reveal: bool = False
    expires_in: Optional[int] = Field(default=1440, description="Expiration in minutes")


class GroupSessionRead(BaseModel):
    id: int
    name: str
    code: str
    max: int
    reveal: bool
    created_at: datetime
    expired: bool

    class Config:
        orm_mode = True