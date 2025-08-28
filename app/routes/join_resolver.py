from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

from app.core.database import SessionDep
from app.models.access_code import AccessCode
from app.models.group_session import GroupSession
from app.models.selection_session import SelectionSession
from app.schemas.join import ResolveJoinRequest, ResolveJoinResponse

router = APIRouter(prefix="/api/join", tags=["Join Resolver"])


@router.post("/resolve", response_model=ResolveJoinResponse)
async def resolve_join(request: ResolveJoinRequest, session: SessionDep):
    code = (request.code or "").strip()
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code is required")

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Find access code
    ac_res = await session.exec(select(AccessCode).where(AccessCode.code == code))
    ac = ac_res.first()
    if not ac or ac.status != "active" or ac.expires_at < now:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access code not found or expired")

    # Check group session
    gs_res = await session.exec(select(GroupSession).where(GroupSession.code_id == ac.id))
    group_session = gs_res.first()

    # Check selection session only if group not found
    selection_session = None
    if not group_session:
        ss_res = await session.exec(select(SelectionSession).where(SelectionSession.code_id == ac.id))
        selection_session = ss_res.first()

    # Collision guard (both found) should not happen because code_id is unique per session
    if group_session and selection_session:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ambiguous access code. Contact support.")

    if group_session:
        return ResolveJoinResponse(
            kind="group",
            next_join_endpoint="/api/groups/join",
            fields_endpoint="/api/groups/fields",
            name=group_session.name,
            identifier=group_session.member_identifier,
        )

    if selection_session:
        return ResolveJoinResponse(
            kind="selection",
            next_join_endpoint="/api/selections/join",
            fields_endpoint="/api/selections/fields",
            name=selection_session.name,
            identifier=selection_session.member_identifier,
        )

    # If neither found
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access code not recognized")
