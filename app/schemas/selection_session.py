# app/schemas/selection_session.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class SelectionSessionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    expires_in: Optional[int] = Field(default=1440, description="Expiration in minutes")
    #fields: List[FieldDefinitionInput]  # Dynamic fields the host wants to collect
    fields: List[str]
    identifier: str
    preferential_rules: Optional[List[PreferentialRuleInput]] = []


class SelectionSessionRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    code_id: str
    max: int
    reveal: bool
    created_at: datetime
    status: str

    class Config:
        orm_mode = True