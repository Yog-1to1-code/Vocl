"""Phase 1 tests: Async SQLite persistence, Google/JWT auth, and per-user daily quota."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from starlette.websockets import WebSocketDisconnect

import app.config as config
import app.db.database as database
import app.db.repository as repository
import app.services.auth as auth_service
import app.services.live_manager as live_manager
import app.services.reasoning_engine as reasoning_engine
from app.db.models import UserRecord
from app.main import app


@pytest.fixture
def isolated_phase1_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "phase1.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setattr(config, "DATABASE_URL", db_url)
    monkeypatch.setattr(config, "USE_MOCK_AI", True)
    monkeypatch.setattr(config, "DEV_AUTH_BYPASS", True)
    monkeypatch.setattr(config, "DAILY_QUOTA_MINUTES", 15.0)
    monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", True)
    monkeypatch.setattr(reasoning_engine, "MOCK_REASONING_LATENCY_SEC", 0.02)
    monkeypatch.setattr(live_manager, "USE_MOCK_AI", True)
    monkeypatch.setattr(live_manager, "_DOWNSTREAM_CHUNK_SEC", 0.002)
    asyncio.run(database.dispose_database())
    asyncio.run(database.init_database(db_url))
    yield db_path
    asyncio.run(database.dispose_database())


def test_unauthenticated_requests_rejected(isolated_phase1_db: Path) -> None:
    with TestClient(app) as client:
        assert client.get("/api/sessions").status_code == 401
        assert client.delete("/api/sessions").status_code == 401
        assert client.get("/api/auth/me").status_code == 401

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws/interview/longest-palindrome"):
                pass
        assert exc_info.value.code == 4401


def test_dev_login_and_me_profile(isolated_phase1_db: Path) -> None:
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/dev-login",
            json={"email": "yogesh@vocl.local", "name": "Yogesh Mali"},
        )
        assert login.status_code == 200
        body = login.json()
        token = body["access_token"]
        assert body["user"]["email"] == "yogesh@vocl.local"
        assert body["user"]["remaining_minutes"] == 15.0

        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["name"] == "Yogesh Mali"
        assert me.json()["daily_minutes_used"] == 0.0


def test_google_login_upserts_user_and_issues_jwt(isolated_phase1_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import app.routers.auth as auth_router

    monkeypatch.setattr(
        auth_router,
        "verify_google_id_token",
        lambda _raw: {
            "sub": "google-sub-12345",
            "email": "candidate@gmail.com",
            "name": "Ada Lovelace",
            "picture": "https://example.com/ada.png",
        },
    )
    with TestClient(app) as client:
        resp = client.post("/api/auth/google", json={"id_token": "fake-google-id-token"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]
        assert data["user"]["email"] == "candidate@gmail.com"
        assert data["user"]["name"] == "Ada Lovelace"


def test_session_events_persisted_and_user_isolation(isolated_phase1_db: Path) -> None:
    with TestClient(app) as client:
        u1 = client.post("/api/auth/dev-login", json={"email": "alice@vocl.local", "name": "Alice"}).json()
        u2 = client.post("/api/auth/dev-login", json={"email": "bob@vocl.local", "name": "Bob"}).json()

        with client.websocket_connect(
            "/ws/interview/longest-palindrome",
            headers={"Authorization": f"Bearer {u1['access_token']}"},
        ) as ws:
            # Drain greeting
            for _ in range(40):
                msg = ws.receive()
                if msg.get("text") and json.loads(msg["text"]).get("status") == "listening":
                    break
            # Trigger 1 mock tool call
            for _ in range(21):
                ws.send_bytes(b"\x00\x00" * 1600)
            for _ in range(40):
                msg = ws.receive()
                if msg.get("text") and json.loads(msg["text"]).get("type") == "tool_result":
                    break
            ws.send_text('{"type": "end_session"}')
            autopsy = None
            for _ in range(40):
                msg = ws.receive()
                if msg.get("text"):
                    payload = json.loads(msg["text"])
                    if payload.get("type") == "autopsy":
                        autopsy = payload
                        break
            assert autopsy is not None

        # Alice sees 1 session; Bob sees 0 (per-user scoping)
        alice_sessions = client.get("/api/sessions", headers={"Authorization": f"Bearer {u1['access_token']}"}).json()
        bob_sessions = client.get("/api/sessions", headers={"Authorization": f"Bearer {u2['access_token']}"}).json()
        assert len(alice_sessions) == 1
        assert len(bob_sessions) == 0

        # Telemetry events recorded in session_events
        events = asyncio.run(repository.list_session_events(autopsy["session_id"]))
        event_types = [e.event_type for e in events]
        assert "tool_call" in event_types
        assert "tool_result" in event_types
        assert "ws_close" in event_types


def test_daily_quota_enforcement_4429_and_date_reset(isolated_phase1_db: Path) -> None:
    with TestClient(app) as client:
        login = client.post("/api/auth/dev-login", json={"email": "quota@vocl.local", "name": "Quota User"}).json()
        user_id = login["user"]["id"]
        token = login["access_token"]

        # Exhaust quota for today -> WebSocket rejects with 4429
        async def _set_quota(minutes: float, days_ago: int = 0) -> None:
            factory = database.get_session_factory()
            target_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).date()
            async with factory() as db:
                await db.execute(
                    update(UserRecord)
                    .where(UserRecord.id == user_id)
                    .values(daily_minutes_used=minutes, quota_reset_date=target_date)
                )
                await db.commit()

        asyncio.run(_set_quota(15.0, days_ago=0))

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/ws/interview/longest-palindrome?token={token}"):
                pass
        assert exc_info.value.code == 4429

        # Roll quota_reset_date back to yesterday -> auto-resets to 0.0 and allows connection
        asyncio.run(_set_quota(15.0, days_ago=1))
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
        assert me["daily_minutes_used"] == 0.0
        assert me["remaining_minutes"] == 15.0

        with client.websocket_connect(f"/ws/interview/longest-palindrome?token={token}") as ws:
            ws.send_text('{"type": "end_session"}')
            for _ in range(30):
                msg = ws.receive()
                if msg.get("text") and json.loads(msg["text"]).get("type") == "autopsy":
                    break
