"""Phase 3 tests: 30-problem commute track, spaced-repetition recommendations, and streak calculation."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

import app.config as config
import app.db.database as database
import app.db.repository as repository
from app.db.models import SessionRecord
from app.main import app
from app.models.schemas import Autopsy
from app.services.recommender import compute_streak_days


@pytest.fixture
def isolated_phase3_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "phase3.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setattr(config, "DATABASE_URL", db_url)
    monkeypatch.setattr(config, "USE_MOCK_AI", True)
    monkeypatch.setattr(config, "DEV_AUTH_BYPASS", True)
    asyncio.run(database.dispose_database())
    asyncio.run(database.init_database(db_url))
    yield db_path
    asyncio.run(database.dispose_database())


def test_thirty_problems_seeded_and_enriched_with_user_stats(isolated_phase3_db: Path) -> None:
    with TestClient(app) as client:
        # Unauthenticated request returns all 30 problems with default stats
        public_resp = client.get("/api/problems")
        assert public_resp.status_code == 200
        problems = public_resp.json()
        assert len(problems) == 30
        assert sum(1 for p in problems if p["category"] == "DSA") == 18
        assert sum(1 for p in problems if p["category"] == "System Design") == 8
        assert sum(1 for p in problems if p["category"] == "Debugging") == 4
        assert all(p["attempts_count"] == 0 and p["best_score"] is None for p in problems)

        # Authenticated user with 2 attempts on longest-palindrome sees enriched stats
        login = client.post("/api/auth/dev-login", json={"email": "track@vocl.local", "name": "Track User"}).json()
        user_id = login["user"]["id"]
        headers = {"Authorization": f"Bearer {login['access_token']}"}

        for sid, score in (("s-1", 5.5), ("s-2", 8.5)):
            asyncio.run(
                repository.record_session_and_increment_quota(
                    user_id,
                    Autopsy(
                        session_id=sid,
                        problem_id="longest-palindrome",
                        duration_sec=180,
                        final_complexity="O(N^2) / O(1)",
                        is_optimal=(score >= 8.0),
                        score=score,
                        correctness_score=score,
                        complexity_score=score,
                        edge_cases_score=score,
                        communication_score=score,
                        missed_edge_cases=[],
                        summary_feedback="Good progress.",
                    ),
                )
            )

        enriched = client.get("/api/problems", headers=headers).json()
        lp = next(p for p in enriched if p["id"] == "longest-palindrome")
        assert lp["attempts_count"] == 2
        assert lp["best_score"] == 8.5
        assert lp["last_practiced_at"] is not None

        unattempted = next(p for p in enriched if p["id"] == "two-sum")
        assert unattempted["attempts_count"] == 0
        assert unattempted["best_score"] is None


def test_recommendations_for_new_and_returning_user(isolated_phase3_db: Path) -> None:
    with TestClient(app) as client:
        # Unauthenticated -> 401
        assert client.get("/api/recommendations").status_code == 401

        login = client.post("/api/auth/dev-login", json={"email": "rec@vocl.local", "name": "Rec User"}).json()
        user_id = login["user"]["id"]
        headers = {"Authorization": f"Bearer {login['access_token']}"}

        # 1. Brand-new user gets 3-drill starter queue
        starter = client.get("/api/recommendations", headers=headers)
        assert starter.status_code == 200
        body = starter.json()
        assert body["weakest_dimension"] is None
        assert body["streak_days"] == 0
        assert len(body["queue"]) == 3
        assert body["queue"][0]["problem_id"] == "two-sum"
        assert body["queue"][2]["category"] == "System Design"

        # 2. Returning user with weak edge_cases + non-optimal session 2 days ago
        asyncio.run(
            repository.record_session_and_increment_quota(
                user_id,
                Autopsy(
                    session_id="rec-s1",
                    problem_id="longest-palindrome",
                    duration_sec=300,
                    final_complexity="O(N^3) / O(1)",
                    is_optimal=False,
                    score=5.0,
                    correctness_score=6.0,
                    complexity_score=5.0,
                    edge_cases_score=3.0,
                    communication_score=7.0,
                    missed_edge_cases=["Empty string", "Even-length palindromes"],
                    summary_feedback="Watch even-length centers.",
                ),
            )
        )

        # Backdate session to 2 days ago to verify spaced retry selection
        async def _backdate(session_id: str, days_ago: int) -> None:
            factory = database.get_session_factory()
            async with factory() as db:
                await db.execute(
                    update(SessionRecord)
                    .where(SessionRecord.id == session_id)
                    .values(created_at=datetime.now(timezone.utc) - timedelta(days=days_ago))
                )
                await db.commit()

        asyncio.run(_backdate("rec-s1", 2))

        rec = client.get("/api/recommendations", headers=headers).json()
        assert rec["weakest_dimension"] == "edge_cases"
        assert rec["dimension_averages"]["edge_cases"] == 3.0
        assert len(rec["queue"]) == 3
        assert rec["queue"][0]["slot"] == "retry"
        assert rec["queue"][0]["problem_id"] == "longest-palindrome"
        assert "Edge Cases" in rec["queue"][0]["reason"]
        # Slot 3 balances with System Design or Debugging
        assert rec["queue"][2]["category"] in ("System Design", "Debugging")


def test_streak_days_calculation_across_multi_day_timestamps() -> None:
    today = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)
    # Consecutive 3-day streak ending today (including multiple sessions on same day)
    ts_3 = [
        today,
        today - timedelta(hours=2),
        today - timedelta(days=1),
        today - timedelta(days=2),
        today - timedelta(days=5),  # gap breaks older history
    ]
    assert compute_streak_days(ts_3, today=today.date()) == 3

    # Streak still alive if practiced yesterday & day before (not yet today)
    ts_yesterday = [today - timedelta(days=1), today - timedelta(days=2)]
    assert compute_streak_days(ts_yesterday, today=today.date()) == 2

    # Gap of >= 2 days resets streak to 0
    assert compute_streak_days([today - timedelta(days=3)], today=today.date()) == 0
    assert compute_streak_days([], today=today.date()) == 0
