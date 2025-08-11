# app/routes/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func, select, and_, or_
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from app.models.group_session import GroupSession
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode
from app.models.group_member import GroupMember
from app.models.selection_member import SelectionMember
from app.models.groups import Group
from app.schemas.dashboard import (
    DashboardOverview, ActiveSessionSummary, AnalyticsData, 
    RecentExport, NotificationItem, SessionStats, UserActivity,
    GeographicData, SessionTrend, ParticipantEngagement
)
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import os
from pathlib import Path

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

class AnalyticsPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SessionType(str, Enum):
    GROUP = "group"
    SELECTION = "selection"
    ALL = "all"

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard overview including key metrics and statistics
    """
    try:
        # Get active sessions count
        active_group_sessions = await session.exec(
            select(func.count(GroupSession.id))
            .join(AccessCode)
            .where(
                and_(
                    GroupSession.host_id == current_user.id,
                    GroupSession.status == "active",
                    AccessCode.expires_at > datetime.now()
                )
            )
        )
        active_group_count = active_group_sessions.one()
        
        active_selection_sessions = await session.exec(
            select(func.count(SelectionSession.id))
            .join(AccessCode)
            .where(
                and_(
                    SelectionSession.host_id == current_user.id,
                    AccessCode.expires_at > datetime.now()
                )
            )
        )
        active_selection_count = active_selection_sessions.one()
        
        # Get total participants across all user's sessions
        group_participants = await session.exec(
            select(func.count(GroupMember.id))
            .join(GroupSession)
            .where(GroupSession.host_id == current_user.id)
        )
        group_participant_count = group_participants.one()
        
        selection_participants = await session.exec(
            select(func.count(SelectionMember.id))
            .join(SelectionSession)
            .where(SelectionSession.host_id == current_user.id)
        )
        selection_participant_count = selection_participants.one()
        
        # Get total sessions created
        total_group_sessions = await session.exec(
            select(func.count(GroupSession.id))
            .where(GroupSession.host_id == current_user.id)
        )
        total_group_count = total_group_sessions.one()
        
        total_selection_sessions = await session.exec(
            select(func.count(SelectionSession.id))
            .where(SelectionSession.host_id == current_user.id)
        )
        total_selection_count = total_selection_sessions.one()
        
        # Get completed groups
        completed_groups = await session.exec(
            select(func.count(Group.id))
            .join(GroupSession)
            .where(GroupSession.host_id == current_user.id)
        )
        completed_groups_count = completed_groups.one()
        
        # Calculate success rate
        total_sessions = total_group_count + total_selection_count
        success_rate = (completed_groups_count / total_sessions * 100) if total_sessions > 0 else 0
        
        return DashboardOverview(
            active_sessions=active_group_count + active_selection_count,
            total_participants=group_participant_count + selection_participant_count,
            sessions_created=total_sessions,
            success_rate=round(success_rate, 2),
            completed_groups=completed_groups_count,
            avg_session_duration=0,  # Will be calculated with session timestamps
            user_country=current_user.country
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard overview: {str(e)}"
        )

@router.get("/sessions/active", response_model=List[ActiveSessionSummary])
async def get_active_sessions(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    session_type: SessionType = Query(SessionType.ALL, description="Filter by session type"),
    limit: int = Query(10, ge=1, le=50, description="Number of sessions to return")
):
    """
    Get list of active sessions with participant counts and quick actions
    """
    try:
        active_sessions = []
        
        if session_type in [SessionType.GROUP, SessionType.ALL]:
            # Get active group sessions
            group_sessions_query = (
                select(GroupSession, AccessCode, func.count(GroupMember.id).label("participant_count"))
                .join(AccessCode, GroupSession.code_id == AccessCode.id)
                .outerjoin(GroupMember, GroupSession.id == GroupMember.group_session_id)
                .where(
                    and_(
                        GroupSession.host_id == current_user.id,
                        GroupSession.status == "active",
                        AccessCode.expires_at > datetime.now()
                    )
                )
                .group_by(GroupSession.id, AccessCode.id)
                .limit(limit)
            )
            
            group_sessions_result = await session.exec(group_sessions_query)
            for group_session, access_code, participant_count in group_sessions_result:
                active_sessions.append(ActiveSessionSummary(
                    id=group_session.id,
                    name=group_session.name,
                    type="group",
                    access_code=access_code.code,
                    participant_count=participant_count or 0,
                    max_participants=None,  # Group sessions don't have max participants
                    status="active",
                    created_at=access_code.created_at,
                    expires_at=access_code.expires_at
                ))
        
        if session_type in [SessionType.SELECTION, SessionType.ALL]:
            # Get active selection sessions
            selection_sessions_query = (
                select(SelectionSession, AccessCode, func.count(SelectionMember.id).label("participant_count"))
                .join(AccessCode, SelectionSession.code_id == AccessCode.id)
                .outerjoin(SelectionMember, SelectionSession.id == SelectionMember.selection_session_id)
                .where(
                    and_(
                        SelectionSession.host_id == current_user.id,
                        AccessCode.expires_at > datetime.now()
                    )
                )
                .group_by(SelectionSession.id, AccessCode.id)
                .limit(limit)
            )
            
            selection_sessions_result = await session.exec(selection_sessions_query)
            for selection_session, access_code, participant_count in selection_sessions_result:
                active_sessions.append(ActiveSessionSummary(
                    id=selection_session.id,
                    name=selection_session.name,
                    type="selection",
                    access_code=access_code.code,
                    participant_count=participant_count or 0,
                    max_participants=selection_session.max_group_size,
                    status="active",
                    created_at=access_code.created_at,
                    expires_at=access_code.expires_at
                ))
        
        # Sort by creation date (most recent first)
        active_sessions.sort(key=lambda x: x.created_at, reverse=True)
        
        return active_sessions[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching active sessions: {str(e)}"
        )

@router.get("/analytics/{period}", response_model=AnalyticsData)
async def get_analytics_data(
    period: AnalyticsPeriod,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    session_type: SessionType = Query(SessionType.ALL, description="Filter analytics by session type")
):
    """
    Get comprehensive analytics data for specified time period
    """
    try:
        # Calculate date range based on period
        now = datetime.now()
        if period == AnalyticsPeriod.DAILY:
            start_date = now - timedelta(days=7)
            date_format = "%Y-%m-%d"
        elif period == AnalyticsPeriod.WEEKLY:
            start_date = now - timedelta(weeks=12)
            date_format = "%Y-W%U"
        elif period == AnalyticsPeriod.MONTHLY:
            start_date = now - timedelta(days=365)
            date_format = "%Y-%m"
        else:  # yearly
            start_date = now - timedelta(days=365*3)
            date_format = "%Y"
        
        # Session creation trends
        session_trends = []
        
        # Get session statistics
        session_stats = SessionStats(
            total_sessions=0,
            group_sessions=0,
            selection_sessions=0,
            completion_rate=0.0,
            avg_participants_per_session=0.0
        )
        
        # Get participant engagement data
        participant_engagement = ParticipantEngagement(
            total_participants=0,
            repeat_participants=0,
            engagement_rate=0.0,
            avg_session_duration=0.0
        )
        
        # Get geographic distribution (simplified)
        geographic_data = [
            GeographicData(country=current_user.country, participant_count=1, session_count=1)
        ]
        
        return AnalyticsData(
            period=period.value,
            session_trends=session_trends,
            session_stats=session_stats,
            participant_engagement=participant_engagement,
            geographic_data=geographic_data,
            generated_at=now
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics data: {str(e)}"
        )

@router.get("/exports/recent", response_model=List[RecentExport])
async def get_recent_exports(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Number of exports to return"),
    file_type: Optional[str] = Query(None, description="Filter by file type (excel, pdf)")
):
    """
    Get list of recent export files with download information
    """
    try:
        recent_exports = []
        
        # Define export directories
        excel_dir = Path("C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/excel_exports")
        pdf_dir = Path("C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/pdf_exports")
        
        export_files = []
        
        # Get Excel exports
        if not file_type or file_type.lower() == "excel":
            if excel_dir.exists():
                for file_path in excel_dir.glob("*.xlsx"):
                    if not file_path.name.startswith("~$"):  # Exclude temp files
                        stat = file_path.stat()
                        export_files.append({
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "file_type": "excel",
                            "file_size": stat.st_size,
                            "created_at": datetime.fromtimestamp(stat.st_ctime)
                        })
        
        # Get PDF exports  
        if not file_type or file_type.lower() == "pdf":
            if pdf_dir.exists():
                for file_path in pdf_dir.glob("*.pdf"):
                    stat = file_path.stat()
                    export_files.append({
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_type": "pdf", 
                        "file_size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime)
                    })
        
        # Sort by creation date (most recent first) and limit
        export_files.sort(key=lambda x: x["created_at"], reverse=True)
        export_files = export_files[:limit]
        
        # Convert to response model
        for export_file in export_files:
            # Extract session info from filename if possible
            session_name = "Unknown Session"
            session_id = None
            
            # Try to parse session info from filename
            filename_parts = export_file["file_name"].split("_")
            if len(filename_parts) >= 2:
                if "group_session" in export_file["file_name"]:
                    session_name = " ".join(filename_parts[2:-2])  # Extract session name
                elif "selection_session" in export_file["file_name"]:
                    session_name = " ".join(filename_parts[2:-2])  # Extract session name
            
            recent_exports.append(RecentExport(
                id=hash(export_file["file_path"]) % 1000000,  # Generate simple ID
                file_name=export_file["file_name"],
                file_type=export_file["file_type"],
                file_size=export_file["file_size"],
                session_name=session_name,
                session_id=session_id,
                created_at=export_file["created_at"],
                download_url=f"/api/export/download/{export_file['file_name']}"
            ))
        
        return recent_exports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent exports: {str(e)}"
        )

@router.get("/notifications", response_model=List[NotificationItem])
async def get_notifications(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return")
):
    """
    Get user notifications including system alerts, session updates, and activity notifications
    """
    try:
        notifications = []
        
        # System notifications (hardcoded for now, would come from a notifications table)
        system_notifications = [
            NotificationItem(
                id=1,
                type="system",
                title="Welcome to GroupifyAssist!",
                message="Your account has been successfully created. Start by creating your first session.",
                is_read=False,
                created_at=datetime.now() - timedelta(hours=1),
                action_url="/sessions/create"
            ),
            NotificationItem(
                id=2,
                type="info",
                title="New Export Feature Available",
                message="You can now export session results in PDF format for professional reports.",
                is_read=False,
                created_at=datetime.now() - timedelta(days=1),
                action_url="/export"
            )
        ]
        
        # Get session-related notifications
        # Check for sessions about to expire
        expiring_sessions_query = (
            select(GroupSession, AccessCode)
            .join(AccessCode)
            .where(
                and_(
                    GroupSession.host_id == current_user.id,
                    GroupSession.status == "active",
                    AccessCode.expires_at > datetime.now(),
                    AccessCode.expires_at < datetime.now() + timedelta(hours=24)
                )
            )
        )
        
        expiring_sessions_result = await session.exec(expiring_sessions_query)
        for group_session, access_code in expiring_sessions_result:
            notifications.append(NotificationItem(
                id=1000 + group_session.id,
                type="warning",
                title="Session Expiring Soon",
                message=f"Your session '{group_session.name}' will expire in less than 24 hours.",
                is_read=False,
                created_at=datetime.now(),
                action_url=f"/sessions/group/{group_session.id}"
            ))
        
        # Add system notifications
        notifications.extend(system_notifications)
        
        # Filter unread if requested
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        # Sort by creation date (most recent first) and limit
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        return notifications[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read
    """
    try:
        # In a real implementation, this would update a notifications table
        # For now, return success
        return {"message": "Notification marked as read", "notification_id": notification_id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )

@router.get("/user-activity", response_model=List[UserActivity])
async def get_user_activity(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(50, ge=1, le=200, description="Number of activities to return")
):
    """
    Get recent user activity across all sessions
    """
    try:
        activities = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Get recent group member joins
        group_joins_query = (
            select(GroupMember, GroupSession)
            .join(GroupSession)
            .where(
                and_(
                    GroupSession.host_id == current_user.id,
                    GroupMember.created_at >= start_date
                )
            )
            .order_by(GroupMember.created_at.desc())
            .limit(limit)
        )
        
        group_joins_result = await session.exec(group_joins_query)
        for member, group_session in group_joins_result:
            activities.append(UserActivity(
                id=f"group_join_{member.id}",
                type="participant_joined",
                description=f"New participant joined '{group_session.name}'",
                session_name=group_session.name,
                session_type="group",
                participant_identifier=getattr(member, 'identifier', 'Unknown'),
                timestamp=member.created_at
            ))
        
        # Get recent selection member joins
        selection_joins_query = (
            select(SelectionMember, SelectionSession)
            .join(SelectionSession)
            .where(
                and_(
                    SelectionSession.host_id == current_user.id,
                    SelectionMember.created_at >= start_date
                )
            )
            .order_by(SelectionMember.created_at.desc())
            .limit(limit)
        )
        
        selection_joins_result = await session.exec(selection_joins_query)
        for member, selection_session in selection_joins_result:
            activities.append(UserActivity(
                id=f"selection_join_{member.id}",
                type="participant_joined",
                description=f"New participant joined '{selection_session.name}'",
                session_name=selection_session.name,
                session_type="selection",
                participant_identifier=getattr(member, 'identifier', 'Unknown'),
                timestamp=member.created_at
            ))
        
        # Sort by timestamp (most recent first) and limit
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        return activities[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user activity: {str(e)}"
        )

@router.get("/quick-stats", response_model=dict)
async def get_quick_stats(
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Get quick statistics for dashboard widgets
    """
    try:
        # Active sessions today
        today = datetime.now().date()
        
        # Sessions created today
        sessions_today_query = select(func.count()).select_from(
            select(GroupSession.id).where(
                and_(
                    GroupSession.host_id == current_user.id,
                    func.date(GroupSession.created_at) == today
                )
            ).union(
                select(SelectionSession.id).where(
                    and_(
                        SelectionSession.host_id == current_user.id,
                        func.date(SelectionSession.created_at) == today
                    )
                )
            ).subquery()
        )
        
        # Participants joined today
        participants_today = 0  # Would calculate from member tables
        
        # Most popular session type
        group_count = await session.exec(
            select(func.count(GroupSession.id)).where(GroupSession.host_id == current_user.id)
        )
        selection_count = await session.exec(
            select(func.count(SelectionSession.id)).where(SelectionSession.host_id == current_user.id)
        )
        
        group_total = group_count.one()
        selection_total = selection_count.one()
        
        most_popular_type = "group" if group_total >= selection_total else "selection"
        
        return {
            "sessions_created_today": 0,  # Would calculate properly
            "participants_joined_today": participants_today,
            "most_popular_session_type": most_popular_type,
            "total_group_sessions": group_total,
            "total_selection_sessions": selection_total,
            "uptime_percentage": 99.9,  # Would come from monitoring
            "last_updated": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching quick stats: {str(e)}"
        )

@router.get("/sessions/{session_id}/participants")
async def get_session_participants(
    session_id: int,
    session_type: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get participants for a specific session with pagination
    """
    try:
        participants = []
        
        if session_type.lower() == "group":
            # Verify session ownership
            group_session = await session.get(GroupSession, session_id)
            if not group_session or group_session.host_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or access denied"
                )
            
            # Get group participants
            participants_query = (
                select(GroupMember)
                .where(GroupMember.group_session_id == session_id)
                .offset(offset)
                .limit(limit)
            )
            
            participants_result = await session.exec(participants_query)
            for participant in participants_result:
                participants.append({
                    "id": participant.id,
                    "identifier": getattr(participant, 'identifier', 'Unknown'),
                    "group_id": getattr(participant, 'group_id', None),
                    "joined_at": participant.created_at,
                    "data": getattr(participant, 'member_data', {})
                })
                
        elif session_type.lower() == "selection":
            # Verify session ownership
            selection_session = await session.get(SelectionSession, session_id)
            if not selection_session or selection_session.host_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or access denied"
                )
            
            # Get selection participants
            participants_query = (
                select(SelectionMember)
                .where(SelectionMember.selection_session_id == session_id)
                .offset(offset)
                .limit(limit)
            )
            
            participants_result = await session.exec(participants_query)
            for participant in participants_result:
                participants.append({
                    "id": participant.id,
                    "identifier": getattr(participant, 'identifier', 'Unknown'),
                    "is_selected": getattr(participant, 'is_selected', False),
                    "joined_at": participant.created_at,
                    "data": getattr(participant, 'member_data', {})
                })
        
        return {
            "session_id": session_id,
            "session_type": session_type,
            "participants": participants,
            "total_count": len(participants),
            "offset": offset,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching session participants: {str(e)}"
        )

@router.get("/sessions/history")
async def get_session_history(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    session_type: SessionType = Query(SessionType.ALL),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get historical sessions with filtering and pagination
    """
    try:
        history = []
        
        if session_type in [SessionType.GROUP, SessionType.ALL]:
            # Get group session history
            group_query = (
                select(GroupSession, AccessCode, func.count(GroupMember.id).label("participant_count"))
                .join(AccessCode, GroupSession.code_id == AccessCode.id)
                .outerjoin(GroupMember, GroupSession.id == GroupMember.group_session_id)
                .where(GroupSession.host_id == current_user.id)
                .group_by(GroupSession.id, AccessCode.id)
            )
            
            if status:
                group_query = group_query.where(GroupSession.status == status)
                
            group_query = group_query.offset(offset).limit(limit)
            group_result = await session.exec(group_query)
            
            for group_session, access_code, participant_count in group_result:
                history.append({
                    "id": group_session.id,
                    "name": group_session.name,
                    "type": "group",
                    "status": group_session.status,
                    "participant_count": participant_count or 0,
                    "created_at": access_code.created_at,
                    "expires_at": access_code.expires_at,
                    "max_group_size": group_session.max_group_size
                })
        
        if session_type in [SessionType.SELECTION, SessionType.ALL]:
            # Get selection session history
            selection_query = (
                select(SelectionSession, AccessCode, func.count(SelectionMember.id).label("participant_count"))
                .join(AccessCode, SelectionSession.code_id == AccessCode.id)
                .outerjoin(SelectionMember, SelectionSession.id == SelectionMember.selection_session_id)
                .where(SelectionSession.host_id == current_user.id)
                .group_by(SelectionSession.id, AccessCode.id)
                .offset(offset)
                .limit(limit)
            )
            
            selection_result = await session.exec(selection_query)
            
            for selection_session, access_code, participant_count in selection_result:
                history.append({
                    "id": selection_session.id,
                    "name": selection_session.name,
                    "type": "selection",
                    "status": "completed" if access_code.expires_at < datetime.now() else "active",
                    "participant_count": participant_count or 0,
                    "created_at": access_code.created_at,
                    "expires_at": access_code.expires_at,
                    "max_group_size": selection_session.max_group_size
                })
        
        # Sort by creation date (most recent first)
        history.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "sessions": history,
            "total_count": len(history),
            "offset": offset,
            "limit": limit,
            "filters": {
                "session_type": session_type.value,
                "status": status
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching session history: {str(e)}"
        )

@router.delete("/sessions/{session_id}/end")
async def end_session(
    session_id: int,
    session_type: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    End/deactivate a session early
    """
    try:
        if session_type.lower() == "group":
            # Get and verify group session
            group_session = await session.get(GroupSession, session_id)
            if not group_session or group_session.host_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or access denied"
                )
            
            # Update session status
            group_session.status = "ended"
            session.add(group_session)
            
            # Expire the access code
            access_code = await session.get(AccessCode, group_session.code_id)
            if access_code:
                access_code.expires_at = datetime.now()
                session.add(access_code)
            
        elif session_type.lower() == "selection":
            # Get and verify selection session
            selection_session = await session.get(SelectionSession, session_id)
            if not selection_session or selection_session.host_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or access denied"
                )
            
            # Expire the access code
            access_code = await session.get(AccessCode, selection_session.code_id)
            if access_code:
                access_code.expires_at = datetime.now()
                session.add(access_code)
        
        await session.commit()
        
        return {
            "message": f"Session {session_id} has been ended successfully",
            "session_id": session_id,
            "session_type": session_type,
            "ended_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending session: {str(e)}"
        )

@router.get("/performance-metrics")
async def get_performance_metrics(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get performance metrics for the dashboard
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Calculate various performance metrics
        metrics = {
            "session_creation_rate": 0.0,  # sessions per day
            "participant_join_rate": 0.0,  # participants per session
            "session_completion_rate": 0.0,  # percentage of completed sessions
            "average_session_duration": 0.0,  # hours
            "peak_usage_hours": [],  # list of hours with highest activity
            "user_retention_rate": 0.0,  # percentage of returning users
            "error_rate": 0.0,  # percentage of failed operations
            "response_time_avg": 0.0,  # average API response time
            "storage_usage": {
                "excel_exports": 0,  # MB
                "pdf_exports": 0,   # MB
                "total_storage": 0  # MB
            },
            "geographic_distribution": [],
            "device_types": {
                "desktop": 0,
                "mobile": 0,
                "tablet": 0
            },
            "period": f"Last {days} days",
            "generated_at": datetime.now()
        }
        
        # Calculate storage usage
        excel_dir = Path("C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/excel_exports")
        pdf_dir = Path("C:/Users/DANIEL/Desktop/animation/Projects/groupifyassist/groupifyassist/pdf_exports")
        
        excel_size = sum(f.stat().st_size for f in excel_dir.glob("*.xlsx") if f.is_file()) / (1024*1024)
        pdf_size = sum(f.stat().st_size for f in pdf_dir.glob("*.pdf") if f.is_file()) / (1024*1024)
        
        metrics["storage_usage"]["excel_exports"] = round(excel_size, 2)
        metrics["storage_usage"]["pdf_exports"] = round(pdf_size, 2)
        metrics["storage_usage"]["total_storage"] = round(excel_size + pdf_size, 2)
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching performance metrics: {str(e)}"
        )
