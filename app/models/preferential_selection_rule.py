# app/models/preferential_grouping_rule.py
from typing import Optional
from sqlmodel import SQLModel, Field

class PreferentialSelectionRule(SQLModel, table=True):
    __tablename__ = "preferential_selection_rules"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    selection_session_id: int = Field(foreign_key="selection_sessions.id")
    field_key: str  # e.g. "gender"
    preference_max_selection: int