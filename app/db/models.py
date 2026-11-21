"""SQLAlchemy ORM models for users, problems, interview sessions, and telemetry events."""
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    google_sub: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    daily_minutes_used: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    quota_reset_date: Mapped[date] = mapped_column(Date, default=_today_utc, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)


class ProblemRecord(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    constraints_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    optimal_complexity: Mapped[str] = mapped_column(String(255), nullable=False)
    edge_cases_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    problem_id: Mapped[str] = mapped_column(String(128), ForeignKey("problems.id"), index=True, nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    correctness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    complexity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    edge_cases_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    communication_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_complexity: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    is_optimal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    missed_edge_cases_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    summary_feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    grading_source: Mapped[str] = mapped_column(String(64), default="system2", nullable=False)
    audio_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)


class SessionEventRecord(Base):
    __tablename__ = "session_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
