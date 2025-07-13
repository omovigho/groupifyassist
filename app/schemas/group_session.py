# app/schemas/group_session.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FieldDefinitionInput(BaseModel):
    field_key: str
    label: str
    data_type: str
    options: Optional[Dict] = None
    required: Optional[bool] = True


class PreferentialRuleInput(BaseModel):
    field_key: str
    max_per_group: int
    
class GroupSessionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max: int
    reveal: bool = False
    expires_in: Optional[int] = Field(default=1440, description="Expiration in minutes")
    group_names: List[str]  # List of group names to create under this session
    #fields: List[FieldDefinitionInput]  # Dynamic fields the host wants to collect
    fields: List[str]
    preferential_rules: Optional[List[PreferentialRuleInput]] = []

class GroupSessionRead(BaseModel):
    id: int
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    access_code_id: int
    max: int
    reveal: bool
    created_at: datetime
    status: str

    class Config:
        orm_mode = True