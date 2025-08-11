# app/schemas/settings.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class UpdateUserProfile(BaseModel):
    country: Optional[str] = None
    # Add other updateable fields as needed

class DashboardSettings(BaseModel):
    theme: Optional[str] = "light"
    dashboard_layout: Optional[str] = "grid"
    default_session_type: Optional[str] = "group"
    show_tutorials: Optional[bool] = True
    auto_refresh_interval: Optional[int] = 30
    default_timezone: Optional[str] = "UTC"
    chart_animations: Optional[bool] = True
    sound_notifications: Optional[bool] = False
    compact_mode: Optional[bool] = False
    sidebar_collapsed: Optional[bool] = False
    language: Optional[str] = "en"
    date_format: Optional[str] = "MM/DD/YYYY"
    time_format: Optional[str] = "12h"
    widget_order: Optional[List[str]] = None
    visible_widgets: Optional[Dict[str, bool]] = None

class NotificationSettings(BaseModel):
    email_notifications: Optional[Dict[str, bool]] = None
    push_notifications: Optional[Dict[str, bool]] = None
    in_app_notifications: Optional[Dict[str, bool]] = None
    notification_frequency: Optional[str] = "immediate"
    quiet_hours: Optional[Dict[str, Any]] = None

class ExportSettings(BaseModel):
    default_format: Optional[str] = "excel"
    include_metadata: Optional[bool] = True
    include_timestamps: Optional[bool] = True
    auto_download: Optional[bool] = False
    retention_days: Optional[int] = 30
    compression: Optional[bool] = False
    password_protection: Optional[bool] = False
    watermark: Optional[bool] = False
    filename_pattern: Optional[str] = "{session_name}_{session_type}_{timestamp}"
    export_quality: Optional[str] = "high"
    include_charts: Optional[bool] = True
    include_summary: Optional[bool] = True

class SecuritySettings(BaseModel):
    two_factor_enabled: Optional[bool] = False
    session_timeout: Optional[int] = 3600
    login_notifications: Optional[bool] = True
    suspicious_activity_alerts: Optional[bool] = True
    ip_restrictions: Optional[Dict[str, Any]] = None

class UserPreferences(BaseModel):
    dashboard: Optional[DashboardSettings] = None
    notifications: Optional[NotificationSettings] = None
    exports: Optional[ExportSettings] = None
    security: Optional[SecuritySettings] = None
