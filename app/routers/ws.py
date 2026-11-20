import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.data.problems import PROBLEMS
from app.services.live_manager import LiveSessionManager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/interview/{problem_id}")
async def interview_websocket(websocket: WebSocket, problem_id: str) -> None:
    if problem_id not in PROBLEMS:
        await websocket.close(code=4004, reason=f"Unknown problem: {problem_id}")
        return

    await websocket.accept()
    logger.info("WebSocket connected for problem %s", problem_id)

    manager = LiveSessionManager(problem_id)
    try:
        autopsy = await manager.run(websocket)
        if autopsy:
            logger.info(
                "Session %s complete — score=%.1f optimal=%s",
                autopsy.session_id,
                autopsy.score,
                autopsy.is_optimal,
            )
    except WebSocketDisconnect:
        logger.info("Client disconnected from problem %s", problem_id)
    except Exception:
        logger.exception("WebSocket handler error for %s", problem_id)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
