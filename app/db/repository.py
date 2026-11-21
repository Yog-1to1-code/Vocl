"""Async repository functions for users, problems, sessions, quotas, and events."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from app.config import settings
from app.data.problems import PROBLEMS
from app.db.database import get_session_factory
from app.db.models import ProblemRecord, SessionEventRecord, SessionRecord, UserRecord
from app.models.schemas import Autopsy, Problem


def _to_problem_schema(row: ProblemRecord) -> Problem:
    return Problem(
        id=row.id,
        title=row.title,
        category=row.category,  # type: ignore[arg-type]
        difficulty=row.difficulty,  # type: ignore[arg-type]
        duration_min=row.duration_min,
        statement=row.prompt_text,
        constraints=json.loads(row.constraints_json or "[]"),
        optimal_complexity=row.optimal_complexity,
        key_edge_cases=json.loads(row.edge_cases_json or "[]"),
    )


async def seed_problems_if_empty() -> None:
    """Upsert all built-in commute track problems idempotently into the database."""
    factory = get_session_factory()
    async with factory() as db:
        existing_rows = {
            row.id: row
            for row in (await db.scalars(select(ProblemRecord))).all()
        }
        for prob in PROBLEMS.values():
            constraints_str = json.dumps(prob.constraints)
            edge_cases_str = json.dumps(prob.key_edge_cases)
            row = existing_rows.get(prob.id)
            if row is None:
                db.add(ProblemRecord(
                    id=prob.id,
                    title=prob.title,
                    category=prob.category,
                    difficulty=prob.difficulty,
                    duration_min=prob.duration_min,
                    prompt_text=prob.statement,
                    constraints_json=constraints_str,
                    optimal_complexity=prob.optimal_complexity,
                    edge_cases_json=edge_cases_str,
                ))
            else:
                row.title = prob.title
                row.category = prob.category
                row.difficulty = prob.difficulty
                row.duration_min = prob.duration_min
                row.prompt_text = prob.statement
                row.constraints_json = constraints_str
                row.optimal_complexity = prob.optimal_complexity
                row.edge_cases_json = edge_cases_str
        await db.commit()


seed_problems = seed_problems_if_empty


async def list_problems(user_id: str | None = None) -> list[Problem]:
    factory = get_session_factory()
    async with factory() as db:
        rows = (await db.scalars(select(ProblemRecord))).all()
        stats_by_problem: dict[str, dict] = {}
        if user_id:
            session_rows = (
                await db.scalars(
                    select(SessionRecord).where(SessionRecord.user_id == user_id)
                )
            ).all()
            for s in session_rows:
                entry = stats_by_problem.setdefault(
                    s.problem_id,
                    {"attempts_count": 0, "best_score": None, "last_practiced_at": None},
                )
                entry["attempts_count"] += 1
                score_val = float(s.overall_score)
                if entry["best_score"] is None or score_val > entry["best_score"]:
                    entry["best_score"] = round(score_val, 1)
                ts_iso = s.created_at.isoformat()
                if entry["last_practiced_at"] is None or ts_iso > entry["last_practiced_at"]:
                    entry["last_practiced_at"] = ts_iso

        # Preserve curated catalog order, appending any extra DB-only rows at the end
        order_index = {pid: idx for idx, pid in enumerate(PROBLEMS.keys())}
        rows_sorted = sorted(rows, key=lambda r: order_index.get(r.id, len(order_index)))
        result: list[Problem] = []
        for row in rows_sorted:
            prob = _to_problem_schema(row)
            stat = stats_by_problem.get(row.id)
            if stat:
                prob.attempts_count = stat["attempts_count"]
                prob.best_score = stat["best_score"]
                prob.last_practiced_at = stat["last_practiced_at"]
            result.append(prob)
        return result


async def list_user_session_records(user_id: str) -> list[SessionRecord]:
    factory = get_session_factory()
    async with factory() as db:
        return list(
            (
                await db.scalars(
                    select(SessionRecord)
                    .where(SessionRecord.user_id == user_id)
                    .order_by(SessionRecord.created_at.asc())
                )
            ).all()
        )


async def get_problem_by_id(problem_id: str) -> Problem | None:
    factory = get_session_factory()
    async with factory() as db:
        row = await db.get(ProblemRecord, problem_id)
        return _to_problem_schema(row) if row else None


async def upsert_user(google_sub: str, email: str, name: str, avatar_url: str = "") -> UserRecord:
    factory = get_session_factory()
    async with factory() as db:
        user = await db.scalar(select(UserRecord).where(UserRecord.google_sub == google_sub))
        if user is None:
            user = UserRecord(
                google_sub=google_sub,
                email=email,
                name=name,
                avatar_url=avatar_url,
                daily_minutes_used=0.0,
                quota_reset_date=datetime.now(timezone.utc).date(),
            )
            db.add(user)
        else:
            user.email = email
            user.name = name
            if avatar_url:
                user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)
        return user


async def get_user_by_id(user_id: str) -> UserRecord | None:
    factory = get_session_factory()
    async with factory() as db:
        return await db.get(UserRecord, user_id)


async def check_and_reset_daily_quota(user_id: str) -> tuple[UserRecord | None, float]:
    """Reset daily_minutes_used when UTC date rolls over and return (user, remaining_minutes)."""
    factory = get_session_factory()
    today = datetime.now(timezone.utc).date()
    async with factory() as db:
        user = await db.get(UserRecord, user_id)
        if user is None:
            return None, 0.0
        if user.quota_reset_date < today:
            user.daily_minutes_used = 0.0
            user.quota_reset_date = today
            await db.commit()
            await db.refresh(user)
        remaining = max(0.0, round(settings.DAILY_QUOTA_MINUTES - user.daily_minutes_used, 2))
        return user, remaining


async def record_session_and_increment_quota(
    user_id: str,
    autopsy: Autopsy,
    audio_path: str | None = None,
    events: list[dict] | None = None,
) -> SessionRecord:
    """Persist completed session, telemetry events, and increment user's daily quota."""
    factory = get_session_factory()
    today = datetime.now(timezone.utc).date()
    async with factory() as db:
        record = SessionRecord(
            id=autopsy.session_id,
            user_id=user_id,
            problem_id=autopsy.problem_id,
            duration_sec=float(autopsy.duration_sec),
            overall_score=autopsy.score,
            correctness_score=autopsy.correctness_score,
            complexity_score=autopsy.complexity_score,
            edge_cases_score=autopsy.edge_cases_score,
            communication_score=autopsy.communication_score,
            final_complexity=autopsy.final_complexity,
            is_optimal=autopsy.is_optimal,
            missed_edge_cases_json=json.dumps(autopsy.missed_edge_cases),
            summary_feedback=autopsy.summary_feedback,
            grading_source=autopsy.grading_source,
            audio_path=audio_path,
        )
        db.add(record)
        # Flush parent SessionRecord before inserting child SessionEventRecord rows (enforced by Postgres FK)
        await db.flush()

        for ev in events or []:
            db.add(SessionEventRecord(
                session_id=autopsy.session_id,
                event_type=str(ev.get("event_type", "unknown")),
                latency_ms=ev.get("latency_ms"),
                payload_json=json.dumps(ev.get("payload", {})),
            ))

        user = await db.get(UserRecord, user_id)
        if user is not None:
            if user.quota_reset_date < today:
                user.daily_minutes_used = 0.0
                user.quota_reset_date = today
            user.daily_minutes_used = round(user.daily_minutes_used + (max(0.0, float(autopsy.duration_sec)) / 60.0), 3)

        await db.commit()
        await db.refresh(record)
        return record


async def list_user_sessions(user_id: str) -> list[dict]:
    factory = get_session_factory()
    async with factory() as db:
        rows = (
            await db.scalars(
                select(SessionRecord)
                .where(SessionRecord.user_id == user_id)
                .order_by(SessionRecord.created_at.asc())
            )
        ).all()
        return [
            {
                "session_id": r.id,
                "timestamp_utc": r.created_at.isoformat(),
                "problem_id": r.problem_id,
                "duration_sec": int(round(r.duration_sec)),
                "final_complexity": r.final_complexity,
                "is_optimal": r.is_optimal,
                "score": r.overall_score,
                "correctness_score": r.correctness_score,
                "complexity_score": r.complexity_score,
                "edge_cases_score": r.edge_cases_score,
                "communication_score": r.communication_score,
                "grading_source": r.grading_source,
                "missed_edge_cases": json.loads(r.missed_edge_cases_json or "[]"),
                "summary_feedback": r.summary_feedback,
            }
            for r in rows
        ]


async def update_session_audio_path(session_id: str, audio_path: str) -> None:
    factory = get_session_factory()
    async with factory() as db:
        row = await db.get(SessionRecord, session_id)
        if row is not None:
            row.audio_path = audio_path
            await db.commit()


async def clear_user_sessions(user_id: str) -> None:
    factory = get_session_factory()
    async with factory() as db:
        session_ids = (
            await db.scalars(select(SessionRecord.id).where(SessionRecord.user_id == user_id))
        ).all()
        if session_ids:
            await db.execute(delete(SessionEventRecord).where(SessionEventRecord.session_id.in_(session_ids)))
            await db.execute(delete(SessionRecord).where(SessionRecord.user_id == user_id))
            await db.commit()


async def list_session_events(session_id: str) -> list[SessionEventRecord]:
    factory = get_session_factory()
    async with factory() as db:
        return list(
            (
                await db.scalars(
                    select(SessionEventRecord)
                    .where(SessionEventRecord.session_id == session_id)
                    .order_by(SessionEventRecord.id.asc())
                )
            ).all()
        )


async def get_user_session(user_id: str, session_id: str) -> SessionRecord | None:
    factory = get_session_factory()
    async with factory() as db:
        return await db.scalar(
            select(SessionRecord).where(
                SessionRecord.id == session_id,
                SessionRecord.user_id == user_id,
            )
        )


def _percentile(sorted_values: list[float], pct: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return round(sorted_values[0], 2)
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = rank - lo
    return round(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac, 2)


async def get_user_metrics_summary(user_id: str) -> dict:
    """Compute session count, reconnect count, and p50/p95 latencies for a user."""
    factory = get_session_factory()
    async with factory() as db:
        session_count = int(
            await db.scalar(
                select(func.count()).select_from(SessionRecord).where(SessionRecord.user_id == user_id)
            )
            or 0
        )
        events = (
            await db.scalars(
                select(SessionEventRecord)
                .join(SessionRecord, SessionEventRecord.session_id == SessionRecord.id)
                .where(SessionRecord.user_id == user_id)
            )
        ).all()

    total_reconnects = sum(1 for ev in events if ev.event_type == "ws_reconnect")
    tool_latencies = sorted(
        float(ev.latency_ms)
        for ev in events
        if ev.event_type == "tool_result" and ev.latency_ms is not None
    )
    grade_latencies = sorted(
        float(ev.latency_ms)
        for ev in events
        if ev.event_type == "final_grade" and ev.latency_ms is not None
    )
    return {
        "session_count": session_count,
        "total_reconnects": total_reconnects,
        "tool_result_p50_ms": _percentile(tool_latencies, 50.0),
        "tool_result_p95_ms": _percentile(tool_latencies, 95.0),
        "final_grade_p50_ms": _percentile(grade_latencies, 50.0),
        "final_grade_p95_ms": _percentile(grade_latencies, 95.0),
    }
