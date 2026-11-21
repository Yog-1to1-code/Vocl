from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.db.models import UserRecord
from app.db.repository import clear_user_sessions, get_problem_by_id, list_problems as db_list_problems, list_user_sessions
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


@router.delete("/sessions")
async def reset_sessions(current_user: UserRecord = Depends(get_current_user)) -> dict[str, str]:
    await clear_user_sessions(current_user.id)
    return {"status": "cleared"}
