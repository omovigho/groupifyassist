from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

class FieldDefinition(SQLModel, table=True):
    __tablename__ = "field_definitions"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="group_sessions.id")
    field_key: str
    label: str
    data_type: str  # e.g. string, number, enum
    #options: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": JSONB})
    options: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    required: bool = Field(default=True)