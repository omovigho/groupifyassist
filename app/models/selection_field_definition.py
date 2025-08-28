from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class SelectionFieldDefinition(SQLModel, table=True):
    __tablename__ = "selection_field_definitions"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    selection_session_id: int = Field(foreign_key="selection_sessions.id")
    field_key: str
    label: str
    data_type: str  # e.g. string, number, enum
    options: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    required: bool = Field(default=True)
