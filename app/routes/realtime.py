# app/routes/realtime.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.dependencies import get_current_user
from app.core.database import get_session, SessionDep
from app.models.user import User
from typing import List
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/api/realtime", tags=["Real-time"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}  # user_id -> websocket

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_text(message)
            except:
                # Connection closed, remove it
                if user_id in self.user_connections:
                    del self.user_connections[user_id]

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/dashboard/{user_id}")
async def websocket_dashboard_updates(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time dashboard updates
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            
            # Handle ping/pong for connection health
            if data == "ping":
                await websocket.send_text("pong")
            
            # Send periodic updates (every 30 seconds)
            await asyncio.sleep(30)
            update_message = {
                "type": "dashboard_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "message": "Dashboard data refreshed",
                    "user_id": user_id
                }
            }
            await websocket.send_text(json.dumps(update_message))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@router.post("/notify/participant-joined")
async def notify_participant_joined(
    session_id: int,
    session_type: str,
    participant_name: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Notify dashboard when a new participant joins a session
    """
    try:
        notification = {
            "type": "participant_joined",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "session_id": session_id,
                "session_type": session_type,
                "participant_name": participant_name,
                "host_id": current_user.id
            }
        }
        
        # Send notification to the session host
        await manager.send_personal_message(
            json.dumps(notification), 
            current_user.id
        )
        
        return {"message": "Notification sent successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )

@router.post("/notify/session-completed")
async def notify_session_completed(
    session_id: int,
    session_type: str,
    groups_formed: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """
    Notify dashboard when a session is completed
    """
    try:
        notification = {
            "type": "session_completed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "session_id": session_id,
                "session_type": session_type,
                "groups_formed": groups_formed,
                "host_id": current_user.id
            }
        }
        
        # Send notification to the session host
        await manager.send_personal_message(
            json.dumps(notification), 
            current_user.id
        )
        
        return {"message": "Session completion notification sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )
