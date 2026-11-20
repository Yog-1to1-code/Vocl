from fastapi import APIRouter

from app.data.problems import PROBLEMS
from app.models.schemas import Problem
from app.services.csv_storage import read_sessions

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/problems")
async def list_problems() -> list[Problem]:
    return list(PROBLEMS.values())


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str) -> Problem:
    return PROBLEMS[problem_id]


@router.get("/sessions")
async def list_sessions() -> list[dict[str, str]]:
    return await read_sessions()
