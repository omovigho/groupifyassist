# app/schemas/selection.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class SelectMembersRequest(BaseModel):
    code: str  # The session access code instead of session_id
    count: int  # Number of members to select
    preferential_selection: Optional[Dict[str, str]] = None  # Field key and value to prioritize


class SelectionResult(BaseModel):
    selected_count: int
    preferential_count: int  # Number selected based on preference
    random_count: int  # Number selected randomly
    member_identifiers: List[str]


class MemberSelectionDetail(BaseModel):
    id: int
    member_identifier: str
    attributes: Dict[str, str]
    selection_type: str  # 'preferential' or 'random'
    selected_at: datetime
