# app/models/preferential_grouping_rule.py
from typing import Optional
from sqlmodel import SQLModel, Field

class PreferentialGroupingRule(SQLModel, table=True):
    __tablename__ = "preferential_grouping_rules"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_session_id: int = Field(foreign_key="group_sessions.id")
    field_key: str  # e.g. "gender"
    max_per_group: int