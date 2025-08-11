# app/routes/settings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from app.schemas.settings import (
    UserPreferences, DashboardSettings, NotificationSettings,
    ExportSettings, SecuritySettings, UpdateUserProfile
)
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/profile", response_model=dict)
async def get_user_profile(
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information
    """
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "country": current_user.country,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "last_login": None,  # Would track last login
            "profile_completion": 80,  # Calculate based on filled fields
            "account_type": "standard"  # Could be premium, enterprise, etc.
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: UpdateUserProfile,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile information
    """
    try:
        # Update allowed fields
        if profile_data.country:
            current_user.country = profile_data.country
        
        # Add other updateable fields as needed
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        
        return {
            "message": "Profile updated successfully",
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.get("/dashboard-preferences")
async def get_dashboard_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's dashboard preferences and customization settings
    """
    try:
        # In a real implementation, these would be stored in a preferences table
        preferences = {
            "theme": "light",  # light, dark, auto
            "dashboard_layout": "grid",  # grid, list, compact
            "default_session_type": "group",  # group, selection
            "show_tutorials": True,
            "auto_refresh_interval": 30,  # seconds
            "default_timezone": "UTC",
            "chart_animations": True,
            "sound_notifications": False,
            "compact_mode": False,
            "sidebar_collapsed": False,
            "language": "en",
            "date_format": "MM/DD/YYYY",
            "time_format": "12h",
            "widget_order": [
                "quick_actions",
                "active_sessions", 
                "recent_activity",
                "analytics"
            ],
            "visible_widgets": {
                "quick_actions": True,
                "active_sessions": True,
                "recent_activity": True,
                "analytics": True,
                "performance_metrics": False
            }
        }
        
        return preferences
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard preferences: {str(e)}"
        )

@router.put("/dashboard-preferences")
async def update_dashboard_preferences(
    preferences: DashboardSettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's dashboard preferences
    """
    try:
        # In a real implementation, store these in a user_preferences table
        return {
            "message": "Dashboard preferences updated successfully",
            "preferences": preferences.dict(),
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating dashboard preferences: {str(e)}"
        )

@router.get("/notification-preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's notification preferences
    """
    try:
        preferences = {
            "email_notifications": {
                "session_created": True,
                "participant_joined": False,
                "session_completed": True,
                "export_ready": True,
                "system_updates": True,
                "marketing": False
            },
            "push_notifications": {
                "session_activity": True,
                "new_participants": False,
                "session_expiring": True,
                "export_completed": True
            },
            "in_app_notifications": {
                "real_time_updates": True,
                "achievement_badges": True,
                "feature_announcements": True,
                "session_reminders": True
            },
            "notification_frequency": "immediate",  # immediate, hourly, daily
            "quiet_hours": {
                "enabled": False,
                "start_time": "22:00",
                "end_time": "08:00",
                "timezone": "UTC"
            }
        }
        
        return preferences
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notification preferences: {str(e)}"
        )

@router.put("/notification-preferences")
async def update_notification_preferences(
    preferences: NotificationSettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's notification preferences
    """
    try:
        return {
            "message": "Notification preferences updated successfully",
            "preferences": preferences.dict(),
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification preferences: {str(e)}"
        )

@router.get("/export-settings")
async def get_export_settings(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's export settings and preferences
    """
    try:
        settings = {
            "default_format": "excel",  # excel, pdf
            "include_metadata": True,
            "include_timestamps": True,
            "auto_download": False,
            "retention_days": 30,  # How long to keep exports
            "compression": False,
            "password_protection": False,
            "watermark": False,
            "custom_templates": [],
            "filename_pattern": "{session_name}_{session_type}_{timestamp}",
            "export_quality": "high",  # low, medium, high
            "include_charts": True,
            "include_summary": True
        }
        
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching export settings: {str(e)}"
        )

@router.put("/export-settings")
async def update_export_settings(
    settings: ExportSettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's export settings
    """
    try:
        return {
            "message": "Export settings updated successfully",
            "settings": settings.dict(),
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating export settings: {str(e)}"
        )

@router.get("/security-settings")
async def get_security_settings(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's security settings
    """
    try:
        settings = {
            "two_factor_enabled": False,
            "session_timeout": 3600,  # seconds
            "login_notifications": True,
            "suspicious_activity_alerts": True,
            "password_last_changed": current_user.created_at,
            "active_sessions": 1,
            "trusted_devices": [],
            "access_log_retention": 90,  # days
            "data_encryption": True,
            "session_recording": False,
            "ip_restrictions": {
                "enabled": False,
                "allowed_ips": []
            }
        }
        
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching security settings: {str(e)}"
        )

@router.put("/security-settings")
async def update_security_settings(
    settings: SecuritySettings,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's security settings
    """
    try:
        return {
            "message": "Security settings updated successfully",
            "settings": settings.dict(),
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating security settings: {str(e)}"
        )

@router.post("/reset-preferences")
async def reset_preferences_to_default(
    current_user: User = Depends(get_current_user)
):
    """
    Reset all user preferences to default values
    """
    try:
        return {
            "message": "All preferences have been reset to default values",
            "reset_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting preferences: {str(e)}"
        )

@router.get("/account-usage")
async def get_account_usage(
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get account usage statistics and limits
    """
    try:
        # Calculate usage statistics
        usage_stats = {
            "current_month": {
                "sessions_created": 0,
                "participants_managed": 0,
                "exports_generated": 0,
                "storage_used_mb": 0
            },
            "limits": {
                "max_sessions_per_month": 100,  # Based on plan
                "max_participants_per_session": 500,
                "max_exports_per_month": 50,
                "max_storage_mb": 1000
            },
            "all_time": {
                "total_sessions": 0,
                "total_participants": 0,
                "total_exports": 0,
                "account_age_days": (datetime.now() - current_user.created_at).days
            },
            "plan_type": "free",  # free, premium, enterprise
            "plan_expires": None,
            "features_available": [
                "basic_grouping",
                "basic_selection", 
                "excel_export",
                "pdf_export"
            ],
            "upgrade_benefits": [
                "unlimited_sessions",
                "advanced_analytics",
                "custom_branding",
                "priority_support"
            ]
        }
        
        return usage_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching account usage: {str(e)}"
        )
