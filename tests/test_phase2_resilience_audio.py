"""Phase 2 tests: WebSocket reconnect grace window, 8kbps mono Opus, Google Drive upload, and latency telemetry."""
from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.db.database as database
import app.db.repository as repository
import app.services.audio_recorder as audio_recorder
import app.services.gdrive_uploader as gdrive_uploader
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


def test_audio_recorder_8kbps_mono_opus_and_wav_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 1 second of 16kHz user PCM + 1 second of 24kHz AI PCM
    pcm_16k = b"\x80\x02" * 16000
    pcm_24k = b"\x00\x08" * 24000

    # Measure raw WAV size first (without ffmpeg)
    rec_ref = audio_recorder.SessionAudioRecorder("sess-ref", recordings_dir=tmp_path)
    rec_ref.record_user_pcm(pcm_16k)
    rec_ref.record_ai_pcm(pcm_24k)
    ref_wav = rec_ref.save_stereo_wav()
    assert ref_wav is not None
    wav_size = ref_wav.stat().st_size

    # 1. Ultra-compact 8 kbps mono VoIP Opus (.ogg) when ffmpeg is available
    if shutil.which("ffmpeg"):
        rec_ogg = audio_recorder.SessionAudioRecorder("sess-opus", recordings_dir=tmp_path)
        rec_ogg.record_user_pcm(pcm_16k)
        rec_ogg.record_ai_pcm(pcm_24k)
        ogg_path = asyncio.run(rec_ogg.save_recording())
        assert ogg_path is not None
        assert ogg_path.suffix == ".ogg"
        assert ogg_path.stat().st_size > 0
        # 8kbps mono VoIP Opus must be drastically smaller than raw stereo 24kHz WAV
        assert ogg_path.stat().st_size < wav_size // 10
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


def test_gdrive_upload_updates_db_deletes_local_and_audio_endpoint_removed(
    isolated_phase2_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recordings_dir = isolated_phase2_db / "recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_file = recordings_dir / "sess-drive-1.ogg"
    audio_file.write_bytes(b"OggS-fake-8kbps-opus-bytes")

    with TestClient(app) as client:
        owner = client.post("/api/auth/dev-login", json={"email": "owner@vocl.local", "name": "Owner"}).json()
        headers = {"Authorization": f"Bearer {owner['access_token']}"}

        autopsy = Autopsy(
            session_id="sess-drive-1",
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
            summary_feedback="You reached expand-around-center cleanly. Next time, check Manacher's bound.",
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

        # User-facing audio endpoint is removed (404) and audio_path omitted from public sessions payload
        assert client.get("/api/sessions/sess-drive-1/audio", headers=headers).status_code == 404
        sessions_list = client.get("/api/sessions", headers=headers).json()
        assert len(sessions_list) == 1
        assert "audio_path" not in sessions_list[0]

        # Mocked Google Drive upload updates DB audio_path -> gdrive:<id> and deletes local file
        monkeypatch.setattr(config.settings, "GDRIVE_CLIENT_ID", "drive-client-id")
        monkeypatch.setattr(config.settings, "GDRIVE_CLIENT_SECRET", "drive-secret")
        monkeypatch.setattr(config.settings, "GDRIVE_REFRESH_TOKEN", "drive-refresh-token")
        monkeypatch.setattr(config.settings, "GDRIVE_FOLDER_ID", "drive-folder-123")
        monkeypatch.setattr(gdrive_uploader, "_refresh_access_token", lambda: "fake-access-token")

        fake_resp = MagicMock()
        fake_resp.json.return_value = {"id": "1AbCdEfGhIjKlMnOp"}
        fake_resp.raise_for_status.return_value = None

        fake_client = AsyncMock()
        fake_client.post.return_value = fake_resp
        fake_client.__aenter__.return_value = fake_client
        fake_client.__aexit__.return_value = None
        monkeypatch.setattr(gdrive_uploader.httpx, "AsyncClient", lambda **_kwargs: fake_client)

        remote_ref = asyncio.run(
            gdrive_uploader.upload_and_cleanup_session_audio("sess-drive-1", "longest-palindrome", audio_file)
        )
        assert remote_ref == "gdrive:1AbCdEfGhIjKlMnOp"
        assert not audio_file.exists()

        row = asyncio.run(repository.get_user_session(owner["user"]["id"], "sess-drive-1"))
        assert row is not None
        assert row.audio_path == "gdrive:1AbCdEfGhIjKlMnOp"

        # Metrics summary still works cleanly
        metrics = client.get("/api/metrics/summary", headers=headers).json()
        assert metrics["session_count"] == 1
        assert metrics["tool_result_p50_ms"] == 420.0
        assert metrics["final_grade_p50_ms"] == 980.0
