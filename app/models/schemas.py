from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Problem(BaseModel):
    id: str
    title: str
    category: Literal["DSA", "System Design", "DevOps"]
    difficulty: Literal["Easy", "Medium", "Hard"]
    duration_min: int
    statement: str
    constraints: list[str]
    optimal_complexity: str
    key_edge_cases: list[str]


class Evaluation(BaseModel):
    time_complexity: str
    space_complexity: str
    is_optimal: bool
    issues: list[str]
    missed_edge_cases: list[str]
    next_socratic_hint: str
    score_delta: float


class Autopsy(BaseModel):
    session_id: str
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    problem_id: str
    duration_sec: int
    final_complexity: str
    is_optimal: bool
    score: float
    missed_edge_cases: list[str]
    summary_feedback: str


class SessionRow(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    problem_id: str = ""
    duration_sec: int = 0
    final_complexity: str = ""
    is_optimal: bool = False
    score: float = 0.0
    missed_edge_cases: str = ""
    summary_feedback: str = ""


class ClientControl(BaseModel):
    type: str
