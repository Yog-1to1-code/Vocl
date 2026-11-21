from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.db.models import UserRecord
from app.db.repository import (
    clear_user_sessions,
    get_problem_by_id,
    get_user_metrics_summary,
    get_user_session,
    list_problems as db_list_problems,
    list_user_sessions,
)
from app.models.schemas import Problem
from app.services.auth import get_current_user

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "ai_mode": "mock" if settings.USE_MOCK_AI else "live"}


@router.get("/problems")
async def list_problems() -> list[Problem]:
    return await db_list_problems()


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str) -> Problem:
    problem = await get_problem_by_id(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail=f"Unknown problem: {problem_id}")
    return problem


@router.get("/sessions")
async def list_sessions(current_user: UserRecord = Depends(get_current_user)) -> list[dict]:
    return await list_user_sessions(current_user.id)


@router.get("/sessions/{session_id}/audio")
async def stream_session_audio(
    session_id: str,
    current_user: UserRecord = Depends(get_current_user),
) -> FileResponse:
    session = await get_user_session(current_user.id, session_id)
    if session is None or not session.audio_path:
        raise HTTPException(status_code=404, detail="Session audio not found")
    audio_file = Path(session.audio_path)
    if not audio_file.is_file():
        raise HTTPException(status_code=404, detail="Session audio file unavailable")
    media_type = "audio/ogg" if audio_file.suffix.lower() == ".ogg" else "audio/wav"
    return FileResponse(path=str(audio_file), media_type=media_type, filename=audio_file.name)


@router.get("/metrics/summary")
async def metrics_summary(current_user: UserRecord = Depends(get_current_user)) -> dict:
    return await get_user_metrics_summary(current_user.id)


@router.delete("/sessions")
async def reset_sessions(current_user: UserRecord = Depends(get_current_user)) -> dict[str, str]:
    await clear_user_sessions(current_user.id)
    return {"status": "cleared"}
