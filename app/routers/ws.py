import logging

from fastapi import APIRouter, WebSocket

from app.data.problems import PROBLEMS
from app.services.live_manager import create_session_bridge

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/interview/{problem_id}")
async def interview_websocket(websocket: WebSocket, problem_id: str) -> None:
    if problem_id not in PROBLEMS:
        await websocket.close(code=4004, reason=f"Unknown problem: {problem_id}")
        return

    await websocket.accept()
    bridge = create_session_bridge(problem_id)
    logger.info("Interview %s started (%s)", problem_id, type(bridge).__name__)
    try:
        autopsy = await bridge.run(websocket)
        logger.info("Session %s complete: score=%.1f optimal=%s", autopsy.session_id, autopsy.score, autopsy.is_optimal)
    except Exception:
        logger.exception("WebSocket handler error for %s", problem_id)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
