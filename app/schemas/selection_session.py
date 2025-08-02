# app/schemas/selection_session.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class PreferentialRuleInput(BaseModel):
    field_key: str
    preference_max_selection: int


class SelectionSessionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    expires_in: Optional[int] = Field(default=1440, description="Expiration in minutes")
    #fields: List[FieldDefinitionInput]  # Dynamic fields the host wants to collect
    fields: List[str]
    max: int
    identifier: str
    preferential_rules: Optional[List[PreferentialRuleInput]] = []


class SelectionSessionRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    code_id: str
    max: int
    created_at: datetime

    class Config:
        orm_mode = True
        

class SelectionJoinRequest(BaseModel):
    code: str
    member_identifier: str
    member_data: Dict[str, str]


class SelectionJoinResponse(BaseModel):
    message: str
    session: str
    member_identifier: str