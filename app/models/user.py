# app/models/user.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password: str
    country: str
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    verification_expires_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
