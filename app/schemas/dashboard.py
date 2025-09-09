# app/schemas/dashboard.py
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class DashboardOverview(BaseModel):
    active_sessions: int
    total_participants: int
    sessions_created: int
    success_rate: float
    completed_groups: int
    avg_session_duration: float
    user_country: str

class ActiveSessionSummary(BaseModel):
    id: int
    name: str
    type: str  # "group" or "selection"
    access_code: str
    participant_count: int
    max_participants: Optional[int]
    status: str
    created_at: datetime
    expires_at: Optional[datetime]

class SessionTrend(BaseModel):
    date: str
    group_sessions: int
    selection_sessions: int
    total_sessions: int

class SessionStats(BaseModel):
    total_sessions: int
    group_sessions: int
    selection_sessions: int
    completion_rate: float
    avg_participants_per_session: float

class ParticipantEngagement(BaseModel):
    total_participants: int
    repeat_participants: int
    engagement_rate: float
    avg_session_duration: float

class GeographicData(BaseModel):
    country: str
    participant_count: int
    session_count: int

class AnalyticsData(BaseModel):
    period: str
    session_trends: List[SessionTrend]
    session_stats: SessionStats
    participant_engagement: ParticipantEngagement
    geographic_data: List[GeographicData]
    generated_at: datetime

class RecentExport(BaseModel):
    id: int
    file_name: str
    file_type: str  # "excel" or "pdf"
    file_size: int
    session_name: str
    session_id: Optional[int]
    created_at: datetime
    download_url: str

class NotificationItem(BaseModel):
    id: int
    type: str  # "info", "warning", "error", "success", "system"
    title: str
    message: str
    is_read: bool
    created_at: datetime
    action_url: Optional[str] = None

class UserActivity(BaseModel):
    id: str
    type: str  # "participant_joined", "session_created", "group_formed", "selection_made"
    description: str
    session_name: str
    session_type: str
    participant_identifier: Optional[str]
    timestamp: datetime


class HostStats(BaseModel):
    """Summary stats for the current host account."""
    active_codes_total: int
    active_codes: List[str]
    total_groups: int
    total_selections: int


class DashboardStats(HostStats):
    """Alias schema for dashboard stats; same fields as HostStats."""
    pass
