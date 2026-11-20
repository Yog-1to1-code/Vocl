from __future__ import annotations

import asyncio
import csv
import os
from pathlib import Path

from app.config import CSV_PATH
from app.models.schemas import SessionRow

_CSV_HEADERS = [
    "session_id",
    "timestamp_utc",
    "problem_id",
    "duration_sec",
    "final_complexity",
    "is_optimal",
    "score",
    "correctness_score",
    "complexity_score",
    "edge_cases_score",
    "communication_score",
    "grading_source",
    "missed_edge_cases",
    "summary_feedback",
]

_lock = asyncio.Lock()


def ensure_csv_exists() -> None:
    path = Path(CSV_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(_CSV_HEADERS)


async def append_session(row: SessionRow) -> None:
    async with _lock:
        ensure_csv_exists()
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                row.session_id,
                row.timestamp_utc,
                row.problem_id,
                row.duration_sec,
                row.final_complexity,
                row.is_optimal,
                row.score,
                row.correctness_score,
                row.complexity_score,
                row.edge_cases_score,
                row.communication_score,
                row.grading_source,
                row.missed_edge_cases,
                row.summary_feedback,
            ])


async def read_sessions() -> list[dict[str, str]]:
    async with _lock:
        ensure_csv_exists()
        with open(CSV_PATH, "r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)


async def clear_sessions() -> None:
    async with _lock:
        path = Path(CSV_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(_CSV_HEADERS)
