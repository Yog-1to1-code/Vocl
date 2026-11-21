import logging

from fastapi import APIRouter, WebSocket

from app.config import settings
from app.db.repository import check_and_reset_daily_quota, get_problem_by_id
from app.services.auth import authenticate_websocket_user
from app.services.live_manager import claim_suspended_session, create_session_bridge, suspend_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/interview/{problem_id}")
async def interview_websocket(websocket: WebSocket, problem_id: str) -> None:
    user = await authenticate_websocket_user(websocket)
    if user is None:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    problem = await get_problem_by_id(problem_id)
    if problem is None:
        await websocket.close(code=4004, reason=f"Unknown problem: {problem_id}")
        return

    user, _remaining = await check_and_reset_daily_quota(user.id)
    if user is None:
        await websocket.close(code=4401, reason="Unauthorized")
        return
    if user.daily_minutes_used >= settings.DAILY_QUOTA_MINUTES:
        await websocket.close(code=4429, reason="Daily quota reached")
        return

    await websocket.accept()
    requested_session_id = websocket.query_params.get("session_id")
    bridge = (
        claim_suspended_session(requested_session_id, user_id=user.id, problem_id=problem_id)
        if requested_session_id
        else None
    )
    is_reconnect = bridge is not None
    if bridge is None:
        bridge = create_session_bridge(problem_id, user_id=user.id)
        logger.info("Interview %s started for user %s (%s)", problem_id, user.email, type(bridge).__name__)
    else:
        bridge.record_reconnect()
        logger.info("Interview %s resumed (session=%s) for user %s", problem_id, bridge.state.session_id, user.email)

    await bridge.send_session_started(websocket, reconnected=is_reconnect)
    try:
        autopsy = await bridge.run(websocket, is_reconnect=is_reconnect)
        if autopsy is None and bridge.was_suspended:
            suspend_session(bridge)
            logger.info("Session %s suspended pending reconnect", bridge.state.session_id)
        elif autopsy is not None:
            logger.info("Session %s complete: score=%.1f optimal=%s", autopsy.session_id, autopsy.score, autopsy.is_optimal)
    except Exception:
        logger.exception("WebSocket handler error for %s", problem_id)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
