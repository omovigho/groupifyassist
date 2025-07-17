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
    description: Optional[str] = None
    code_id: str
    max: int
    reveal: bool
    created_at: datetime
    status: str

    class Config:
        orm_mode = True
        
class GroupJoinRequest(BaseModel):
    code: str
    member_identifier: str
    member_data: Dict[str, str]


class GroupJoinResponse(BaseModel):
    message: str
    group_name: str
    session: str
    member_identifier: str
    
    
class MessageResponse(BaseModel):
    message: str