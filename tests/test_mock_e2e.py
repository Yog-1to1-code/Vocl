from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_AI"] = "true"

import app.config as config
import app.db.database as database
import app.services.live_manager as live_manager
import app.services.reasoning_engine as reasoning_engine
from app.main import app


@pytest.fixture(autouse=True)
def isolated_mock_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    test_db = tmp_path / "vocl_test.db"
    db_url = f"sqlite+aiosqlite:///{test_db}"
    monkeypatch.setattr(config, "USE_MOCK_AI", True)
    monkeypatch.setattr(config, "DATABASE_URL", db_url)
    monkeypatch.setattr(config, "DEV_AUTH_BYPASS", True)
    monkeypatch.setattr(config, "DAILY_QUOTA_MINUTES", 15.0)
    monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", True)
    monkeypatch.setattr(reasoning_engine, "MOCK_REASONING_LATENCY_SEC", 0.05)
    monkeypatch.setattr(live_manager, "USE_MOCK_AI", True)
    monkeypatch.setattr(live_manager, "_DOWNSTREAM_CHUNK_SEC", 0.005)
    asyncio.run(database.dispose_database())
    asyncio.run(database.init_database(db_url))
    yield test_db
    asyncio.run(database.dispose_database())


def _dev_auth_headers(client: TestClient, email: str = "dev@vocl.local") -> tuple[dict[str, str], str]:
    resp = client.post("/api/auth/dev-login", json={"email": email, "name": "Dev User"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, token


def _drain_turn_until_listening(ws) -> tuple[list[dict], int]:
    """Read messages from the WebSocket until state transitions to listening."""
    json_frames: list[dict] = []
    pcm_bytes = 0
    for _ in range(60):
        message = ws.receive()
        if message.get("bytes") is not None:
            pcm_bytes += len(message["bytes"])
        elif message.get("text") is not None:
            payload = json.loads(message["text"])
            json_frames.append(payload)
            if payload.get("type") == "state" and payload.get("status") == "listening":
                break
    return json_frames, pcm_bytes


def test_health_and_problems_catalog() -> None:
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        problems = client.get("/api/problems")
        assert problems.status_code == 200
        items = problems.json()
        assert len(items) == 3
        assert {p["id"] for p in items} == {"url-shortener", "longest-palindrome", "postgres-cpu-spike"}

        dev_page = client.get("/dev-test")
        assert dev_page.status_code == 200
        assert "Vocl" in dev_page.text


def test_mock_system2_all_three_problems() -> None:
    from app.data.problems import PROBLEMS

    for _problem_id, problem in PROBLEMS.items():
        evaluation = asyncio.run(
            reasoning_engine.evaluate_candidate_approach(problem, "Brute force initial idea")
        )
        assert evaluation.is_optimal is False
        assert len(evaluation.issues) >= 1
        assert len(evaluation.missed_edge_cases) >= 1
        assert len(evaluation.next_socratic_hint) >= 10
        assert evaluation.score_delta > 0.0


def test_websocket_mock_audio_tool_call_and_db_autopsy(isolated_mock_env: Path) -> None:
    with TestClient(app) as client:
        headers, token = _dev_auth_headers(client)

        with client.websocket_connect(f"/ws/interview/longest-palindrome?token={token}") as ws:
            # 1. Initial greeting turn: speaking -> binary 24kHz PCM -> listening
            greeting_frames, greeting_pcm_bytes = _drain_turn_until_listening(ws)
            greeting_states = [f["status"] for f in greeting_frames if f.get("type") == "state"]
            assert greeting_states[0] == "speaking"
            assert greeting_states[-1] == "listening"
            assert greeting_pcm_bytes == len(live_manager.GREETING_CHIME_PCM)

            # 2. Stream >64,000 bytes (~2s) of 16kHz PCM in 100ms (3,200-byte) chunks
            pcm_chunk = b"\x00\x00" * 1600
            for _ in range(21):
                ws.send_bytes(pcm_chunk)

            turn_frames, hint_pcm_bytes = _drain_turn_until_listening(ws)
            turn_states = [f["status"] for f in turn_frames if f.get("type") == "state"]
            assert turn_states == ["analyzing", "speaking", "listening"]
            assert hint_pcm_bytes == len(live_manager.HINT_CHIME_PCM)

            tool_results = [f for f in turn_frames if f.get("type") == "tool_result"]
            assert len(tool_results) == 1
            assert tool_results[0]["time_complexity"] == "O(N^3)"
            assert tool_results[0]["is_optimal"] is False

            # 3. Verify barge-in hook emits clear_audio_buffer
            ws.send_text(json.dumps({"type": "simulate_barge_in"}))
            barge_frame = json.loads(ws.receive_text())
            assert barge_frame["type"] == "clear_audio_buffer"

            # 4. End session and verify autopsy frame
            ws.send_text(json.dumps({"type": "end_session"}))
            autopsy = None
            for _ in range(20):
                frame = json.loads(ws.receive_text())
                if frame.get("type") == "autopsy":
                    autopsy = frame
                    break

            assert autopsy is not None
            assert autopsy["problem_id"] == "longest-palindrome"
            assert autopsy["final_complexity"] == "O(N^3) / O(1)"
            assert autopsy["is_optimal"] is False
            assert autopsy["score"] == 4.5
            assert len(autopsy["missed_edge_cases"]) >= 1

        # 5. Confirm row persisted to SQLite and returned by authenticated GET /api/sessions
        assert isolated_mock_env.exists()
        sessions_resp = client.get("/api/sessions", headers=headers)
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()
        assert len(sessions) == 1
        assert sessions[0]["problem_id"] == "longest-palindrome"
        assert sessions[0]["final_complexity"] == "O(N^3) / O(1)"


def test_delete_sessions_clears_user_db_rows(isolated_mock_env: Path) -> None:
    with TestClient(app) as client:
        headers, token = _dev_auth_headers(client)
        with client.websocket_connect(f"/ws/interview/url-shortener?token={token}") as ws:
            ws.send_text('{"type": "end_session"}')
            for _ in range(20):
                msg = ws.receive()
                if msg.get("text") and json.loads(msg["text"]).get("type") == "autopsy":
                    break

        assert len(client.get("/api/sessions", headers=headers).json()) == 1

        reset_resp = client.delete("/api/sessions", headers=headers)
        assert reset_resp.status_code == 200
        assert reset_resp.json() == {"status": "cleared"}
        assert client.get("/api/sessions", headers=headers).json() == []
