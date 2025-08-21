from fastapi import FastAPI, Depends, HTTPException, Request
from app.core.dependencies import get_current_user
from app.core.database import get_session
from sqlmodel import select
from app.models.selection_session import SelectionSession
from app.models.access_code import AccessCode
import asyncio

async def check_session():
    async for db_session in get_session():
        # Check if selection session with ID 1 exists
        result = await db_session.exec(
            select(SelectionSession, AccessCode)
            .where(
                (SelectionSession.id == 1) &
                (SelectionSession.code_id == AccessCode.id)
            )
        )
        session_data = result.first()
        
        if session_data:
            session, access_code = session_data
            print("\nSelection Session Found:")
            print(f"  ID: {session.id}")
            print(f"  Name: {session.name}")
            print(f"  Host ID: {session.host_id}")
            print(f"  Access Code: {access_code.code}")
            print(f"  Member Identifier: {session.member_identifier}")
            print(f"  Max Group Size: {session.max_group_size}")
        else:
            print("\nNo selection session found with ID 1")
            
        # List all selection sessions
        all_sessions = await db_session.exec(select(SelectionSession))
        sessions = all_sessions.all()
        
        if sessions:
            print("\nAll Selection Sessions:")
            for sess in sessions:
                print(f"  ID: {sess.id}, Name: {sess.name}, Host ID: {sess.host_id}")
        else:
            print("\nNo selection sessions exist in the database")
            
        break  # We only need to check once

if __name__ == "__main__":
    asyncio.run(check_session())
