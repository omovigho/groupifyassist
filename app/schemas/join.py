from pydantic import BaseModel
from typing import Literal, Optional


class ResolveJoinRequest(BaseModel):
    code: str


class ResolveJoinResponse(BaseModel):
    kind: Literal["group", "selection"]
    next_join_endpoint: str
    fields_endpoint: str
    # Optional minimal display info
    name: Optional[str] = None
    identifier: Optional[str] = None
