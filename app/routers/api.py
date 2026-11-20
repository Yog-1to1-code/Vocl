from fastapi import APIRouter, HTTPException

from app.config import settings
from app.data.problems import PROBLEMS
from app.models.schemas import Problem
from app.services.csv_storage import read_sessions

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "ai_mode": "mock" if settings.USE_MOCK_AI else "live"}


@router.get("/problems")
async def list_problems() -> list[Problem]:
    return list(PROBLEMS.values())


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str) -> Problem:
    if problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail=f"Unknown problem: {problem_id}")
    return PROBLEMS[problem_id]


@router.get("/sessions")
async def list_sessions() -> list[dict[str, str]]:
    return await read_sessions()
