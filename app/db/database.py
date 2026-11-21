"""Async SQLAlchemy engine and session factory (SQLite default, PostgreSQL-ready)."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_active_url: str = ""


def _ensure_sqlite_parent_dir(url: str) -> None:
    if not url.startswith("sqlite"):
        return
    # Extract local filesystem path from sqlite+aiosqlite:///./data/vocl.db
    raw_path = url.split(":///", 1)[-1]
    if raw_path and raw_path != ":memory:":
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


def configure_database(url: str | None = None) -> AsyncEngine:
    """Initialize or reconfigure the async engine (used by startup and isolated tests)."""
    global _engine, _session_factory, _active_url
    target_url = url or settings.DATABASE_URL
    if _engine is not None and target_url == _active_url:
        return _engine

    _ensure_sqlite_parent_dir(target_url)
    _engine = create_async_engine(target_url, future=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    _active_url = target_url
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None or _active_url != settings.DATABASE_URL:
        configure_database(settings.DATABASE_URL)
    assert _session_factory is not None
    return _session_factory


async def init_database(url: str | None = None) -> None:
    """Create tables if missing and seed the problem catalog idempotently."""
    from app.db import models  # noqa: F401 — register ORM metadata
    from app.db.repository import seed_problems_if_empty

    engine = configure_database(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_problems_if_empty()


async def dispose_database() -> None:
    global _engine, _session_factory, _active_url
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
    _active_url = ""
