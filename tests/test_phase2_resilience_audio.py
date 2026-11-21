"""Phase 2 tests: WebSocket reconnect grace window, Opus/WAV audio streaming, and latency telemetry."""
from __future__ import annotations

import asyncio
import json
import shutil
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.db.database as database
import app.db.repository as repository
import app.services.audio_recorder as audio_recorder
import app.services.live_manager as live_manager
import app.services.reasoning_engine as reasoning_engine
from app.main import app
from app.models.schemas import Autopsy


@pytest.fixture
def isolated_phase2_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "phase2.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setattr(config, "DATABASE_URL", db_url)
    monkeypatch.setattr(config, "USE_MOCK_AI", True)
    monkeypatch.setattr(config, "DEV_AUTH_BYPASS", True)
    monkeypatch.setattr(config, "DAILY_QUOTA_MINUTES", 15.0)
    monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", True)
    monkeypatch.setattr(reasoning_engine, "MOCK_REASONING_LATENCY_SEC", 0.01)
    monkeypatch.setattr(live_manager, "USE_MOCK_AI", True)
    monkeypatch.setattr(live_manager, "_DOWNSTREAM_CHUNK_SEC", 0.002)
    monkeypatch.setattr(live_manager, "RECONNECT_GRACE_SEC", 5.0)
    live_manager.clear_suspended_sessions()
    asyncio.run(database.dispose_database())
    asyncio.run(database.init_database(db_url))
    yield tmp_path
    live_manager.clear_suspended_sessions()
    asyncio.run(database.dispose_database())


def test_ws_unexpected_disconnect_and_reconnect_within_grace_window(isolated_phase2_db: Path) -> None:
    with TestClient(app) as client:
        login = client.post("/api/auth/dev-login", json={"email": "commuter@vocl.local", "name": "Commuter"}).json()
        token = login["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Connect, capture session_id, then disconnect unexpectedly (no end_session)
        session_id = None
        with client.websocket_connect("/ws/interview/longest-palindrome", headers=headers) as ws1:
            for _ in range(20):
                msg = ws1.receive()
                if msg.get("text"):
                    payload = json.loads(msg["text"])
                    if payload.get("type") == "session_started":
                        session_id = payload["session_id"]
                    if payload.get("status") == "listening":
                        break
        assert session_id is not None

        # Reconnect with the same session_id within the grace window
        reconnected_status = None
        autopsy = None
        with client.websocket_connect(
            f"/ws/interview/longest-palindrome?session_id={session_id}",
            headers=headers,
        ) as ws2:
            for _ in range(15):
                msg = ws2.receive()
                if msg.get("text"):
                    payload = json.loads(msg["text"])
                    if payload.get("type") == "status" and payload.get("reconnected") is True:
                        reconnected_status = payload
                        break
            assert reconnected_status is not None
            assert reconnected_status["status"] == "listening"

            # Trigger 1 tool call, then end cleanly
            for _ in range(21):
                ws2.send_bytes(b"\x00\x00" * 1600)
            for _ in range(40):
                msg = ws2.receive()
                if msg.get("text") and json.loads(msg["text"]).get("type") == "tool_result":
                    break
            ws2.send_text('{"type": "end_session"}')
            for _ in range(40):
                msg = ws2.receive()
                if msg.get("text"):
                    payload = json.loads(msg["text"])
                    if payload.get("type") == "autopsy":
                        autopsy = payload
                        break

        assert autopsy is not None
        assert autopsy["session_id"] == session_id

        events = asyncio.run(repository.list_session_events(session_id))
        event_types = [ev.event_type for ev in events]
        assert "ws_reconnect" in event_types
        assert "tool_result" in event_types
        assert "ws_close" in event_types

        metrics = client.get("/api/metrics/summary", headers=headers)
        assert metrics.status_code == 200
        summary = metrics.json()
        assert summary["session_count"] == 1
        assert summary["total_reconnects"] == 1
        assert summary["tool_result_p50_ms"] is not None
        assert summary["tool_result_p95_ms"] is not None


def test_audio_recorder_opus_and_wav_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pcm_16k = b"\x10\x00" * 4000  # 0.25s
    pcm_24k = b"\x20\x00" * 6000  # 0.25s

    # 1. Opus (.ogg) when ffmpeg is available on PATH
    if shutil.which("ffmpeg"):
        rec_ogg = audio_recorder.SessionAudioRecorder("sess-opus", recordings_dir=tmp_path)
        rec_ogg.record_user_pcm(pcm_16k)
        rec_ogg.record_ai_pcm(pcm_24k)
        ogg_path = asyncio.run(rec_ogg.save_recording())
        assert ogg_path is not None
        assert ogg_path.suffix == ".ogg"
        assert ogg_path.stat().st_size > 0
        assert not (tmp_path / "sess-opus.wav").exists()

    # 2. Automatic WAV fallback when ffmpeg is missing
    monkeypatch.setattr(audio_recorder.shutil, "which", lambda _cmd: None)
    rec_wav = audio_recorder.SessionAudioRecorder("sess-wav", recordings_dir=tmp_path)
    rec_wav.record_user_pcm(pcm_16k)
    rec_wav.record_ai_pcm(pcm_24k)
    wav_path = asyncio.run(rec_wav.save_recording())
    assert wav_path is not None
    assert wav_path.suffix == ".wav"
    assert wav_path.stat().st_size > 44


def test_authenticated_audio_streaming_and_ownership_isolation(isolated_phase2_db: Path) -> None:
    recordings_dir = isolated_phase2_db / "recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_file = recordings_dir / "sess-audio-1.ogg"
    audio_file.write_bytes(b"OggS-fake-opus-stream-bytes")

    with TestClient(app) as client:
        owner = client.post("/api/auth/dev-login", json={"email": "owner@vocl.local", "name": "Owner"}).json()
        other = client.post("/api/auth/dev-login", json={"email": "other@vocl.local", "name": "Other"}).json()

        autopsy = Autopsy(
            session_id="sess-audio-1",
            problem_id="longest-palindrome",
            duration_sec=45,
            final_complexity="O(N^2) / O(1)",
            is_optimal=False,
            score=7.5,
            correctness_score=8.0,
            complexity_score=7.0,
            edge_cases_score=7.0,
            communication_score=8.0,
            grading_source="gemini_live",
            missed_edge_cases=[],
            summary_feedback="Solid expand-around-center solution.",
        )
        asyncio.run(
            repository.record_session_and_increment_quota(
                owner["user"]["id"],
                autopsy,
                audio_path=str(audio_file),
                events=[
                    {"event_type": "tool_result", "latency_ms": 420.0, "payload": {}},
                    {"event_type": "final_grade", "latency_ms": 980.0, "payload": {}},
                    {"event_type": "ws_close", "latency_ms": None, "payload": {"close_code": 1000}},
                ],
            )
        )

        # Unauthenticated -> 401
        assert client.get("/api/sessions/sess-audio-1/audio").status_code == 401

        # Different user -> 404
        assert client.get(
            "/api/sessions/sess-audio-1/audio",
            headers={"Authorization": f"Bearer {other['access_token']}"},
        ).status_code == 404

        # Owner -> 200 audio/ogg
        resp = client.get(
            "/api/sessions/sess-audio-1/audio",
            headers={"Authorization": f"Bearer {owner['access_token']}"},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("audio/ogg")
        assert resp.content == b"OggS-fake-opus-stream-bytes"

        # Metrics summary includes final_grade p50/p95
        metrics = client.get(
            "/api/metrics/summary",
            headers={"Authorization": f"Bearer {owner['access_token']}"},
        ).json()
        assert metrics["session_count"] == 1
        assert metrics["tool_result_p50_ms"] == 420.0
        assert metrics["final_grade_p50_ms"] == 980.0
        assert metrics["final_grade_p95_ms"] == 980.0
