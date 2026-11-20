"""
Pre-flight quota-safety audit tests for Vocl.
Verifies live config, schemas, non-blocking tool calling, and guardrails without external API calls.
"""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.genai import types

from app.config import (
    GEMINI_LIVE_MODEL,
    GEMINI_REASONING_MODEL,
    PROMPT_MODE,
    SESSION_MAX_DURATION_SEC,
    SYSTEM2_TIMEOUT_SEC,
)
from app.data.problems import PROBLEMS
from app.models.schemas import Evaluation, Problem
from app.prompts import build_live_system_prompt, build_reasoning_system_prompt
from app.services.live_manager import (
    _BEHAVIOR_NON_BLOCKING,
    _EVALUATE_APPROACH_DECLARATION,
    _SCHEDULING_INTERRUPT,
    LiveSessionManager,
    MockLiveSessionManager,
)


def test_gemini_models_and_session_cap():
    """Verify configured model names and timeout guardrails."""
    assert GEMINI_LIVE_MODEL == "gemini-3.8-live"
    assert GEMINI_REASONING_MODEL == "gemini-3.1-flash-lite"
    assert SESSION_MAX_DURATION_SEC == 900
    assert SYSTEM2_TIMEOUT_SEC == 3.0


def test_evaluate_approach_declaration_schema():
    """Verify tool declaration schema and non-blocking behavior."""
    decl = _EVALUATE_APPROACH_DECLARATION
    assert decl.name == "evaluate_approach"
    assert "problem_id" in decl.parameters.properties
    assert "user_approach_summary" in decl.parameters.properties
    assert set(decl.parameters.required) == {"problem_id", "user_approach_summary"}

    # Assert non-blocking behavior if google-genai supports it
    if hasattr(types, "Behavior") and hasattr(types.Behavior, "NON_BLOCKING"):
        assert decl.behavior == types.Behavior.NON_BLOCKING
        assert _BEHAVIOR_NON_BLOCKING == types.Behavior.NON_BLOCKING


def test_live_session_manager_config_dry_run(monkeypatch):
    """Verify LiveConnectConfig builds without TypeError or schema errors."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-preflight-key")
    manager = LiveSessionManager("longest-palindrome")
    config = manager._build_live_config()

    assert types.Modality.AUDIO in config.response_modalities
    assert len(config.tools) == 1
    decl_names = [d.name for d in config.tools[0].function_declarations]
    assert decl_names == ["evaluate_approach", "submit_final_grade"]
    assert config.input_audio_transcription is not None
    assert config.output_audio_transcription is not None
    assert "Vocl" in config.system_instruction
    assert "longest-palindrome" in config.system_instruction or "Longest Palindromic" in config.system_instruction


def test_reasoning_engine_config_dry_run():
    """Verify System 2 GenerateContentConfig constructs cleanly with JSON schema."""
    problem = PROBLEMS["url-shortener"]
    sys_prompt = build_reasoning_system_prompt(problem)
    assert "System 2" in sys_prompt
    assert problem.title in sys_prompt
    assert problem.optimal_complexity in sys_prompt

    config = types.GenerateContentConfig(
        system_instruction=sys_prompt,
        response_mime_type="application/json",
        response_schema=Evaluation,
        temperature=0.1,
    )
    assert config.response_mime_type == "application/json"
    assert config.response_schema is Evaluation
    assert config.temperature == 0.1


def test_tool_call_in_flight_guard():
    """Verify that concurrent or rapid duplicate tool calls are debounced."""
    async def _test():
        manager = LiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()
        session_mock = MagicMock()

        call1 = MagicMock()
        call1.id = "call_1"
        call1.name = "evaluate_approach"
        call1.args = {"user_approach_summary": "First idea"}

        call2 = MagicMock()
        call2.id = "call_2"
        call2.name = "evaluate_approach"
        call2.args = {"user_approach_summary": "Duplicate rapid idea"}

        tool_call_obj = MagicMock()
        tool_call_obj.function_calls = [call1, call2]

        # First call will be dispatched
        manager._dispatch_tool_call(ws_mock, session_mock, tool_call_obj)
        # Background task should be created for call1 only; call2 is ignored as in-flight
        assert len(manager._background_tasks) == 1

        # Immediate second dispatch is also ignored due to in-flight or debounce timestamp
        tool_call_obj2 = MagicMock()
        tool_call_obj2.function_calls = [call1]
        manager._dispatch_tool_call(ws_mock, session_mock, tool_call_obj2)
        assert len(manager._background_tasks) == 1

        # Cleanup created background tasks
        for task in manager._background_tasks:
            task.cancel()
        await asyncio.gather(*manager._background_tasks, return_exceptions=True)

    asyncio.run(_test())


def test_mock_non_blocking_tool_call_execution():
    """Verify MockLiveSessionManager handles non-blocking tool calls and cancels cleanly."""
    async def _test():
        manager = MockLiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()

        # Trigger mock tool turn
        await manager._record_evaluation(ws_mock, "Test summary")
        assert len(manager.state.evaluations) == 1
        assert manager.state.evaluations[0].is_optimal is False

        # Verify cancel cleanup does not raise
        await manager._cancel_active_turn()

    asyncio.run(_test())


def test_concurrent_websocket_writes_serialized():
    """Verify _ws_write_lock prevents overlapping send_text / send_bytes frames."""
    async def _test():
        manager = LiveSessionManager("longest-palindrome")
        active_writers = 0
        overlap_detected = False

        async def _guarded_write(*_args, **_kwargs):
            nonlocal active_writers, overlap_detected
            active_writers += 1
            if active_writers > 1:
                overlap_detected = True
            await asyncio.sleep(0.005)
            active_writers -= 1

        ws_mock = MagicMock()
        ws_mock.send_text = AsyncMock(side_effect=_guarded_write)
        ws_mock.send_bytes = AsyncMock(side_effect=_guarded_write)

        await asyncio.gather(
            *[manager._send_json(ws_mock, {"type": "state", "status": "listening"}) for _ in range(5)],
            *[manager._send_bytes(ws_mock, b"\x00\x00" * 160) for _ in range(5)],
        )
        assert overlap_detected is False
        assert ws_mock.send_text.call_count == 5
        assert ws_mock.send_bytes.call_count == 5

    asyncio.run(_test())


def test_end_session_during_in_flight_tool_call(monkeypatch):
    """Verify closing session mid-evaluation cancels background task without calling send_tool_response."""
    import app.services.reasoning_engine as reasoning_engine

    async def _test():
        monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", True)
        monkeypatch.setattr(reasoning_engine, "MOCK_REASONING_LATENCY_SEC", 0.3)

        manager = LiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()
        session_mock = MagicMock()
        session_mock.send_tool_response = AsyncMock()

        call = MagicMock()
        call.id = "call_inflight_1"
        call.name = "evaluate_approach"
        call.args = {"user_approach_summary": "In-flight approach"}
        tool_call = MagicMock()
        tool_call.function_calls = [call]

        manager._dispatch_tool_call(ws_mock, session_mock, tool_call)
        assert manager._tool_call_in_flight is True
        await asyncio.sleep(0.05)

        # Simulate session teardown while evaluation is still running
        manager._closed = True
        for bg in list(manager._background_tasks):
            bg.cancel()
        await asyncio.gather(*manager._background_tasks, return_exceptions=True)

        assert manager._tool_call_in_flight is False
        session_mock.send_tool_response.assert_not_called()

    asyncio.run(_test())


def test_zero_evaluation_early_exit_and_404_routes(tmp_path, monkeypatch):
    """Verify 0-evaluation early exit produces valid Autopsy and invalid problem IDs return 404."""
    from fastapi.testclient import TestClient
    import app.services.csv_storage as csv_storage
    from app.main import app

    monkeypatch.setattr(csv_storage, "CSV_PATH", str(tmp_path / "early_exit.csv"))
    client = TestClient(app)

    # Unknown problem via REST returns 404 instead of unhandled KeyError
    resp = client.get("/api/problems/nonexistent-problem")
    assert resp.status_code == 404

    # Early exit before any approach is proposed
    with client.websocket_connect("/ws/interview/url-shortener") as ws:
        ws.send_text('{"type": "end_session"}')
        autopsy = None
        for _ in range(30):
            msg = ws.receive()
            if msg.get("text"):
                payload = __import__("json").loads(msg["text"])
                if payload.get("type") == "autopsy":
                    autopsy = payload
                    break
        assert autopsy is not None
        assert autopsy["problem_id"] == "url-shortener"
        assert autopsy["final_complexity"] == "Not evaluated"
        assert autopsy["score"] == 0.0
        assert autopsy["is_optimal"] is False
        assert autopsy["timestamp_utc"]


def test_upstream_audio_flows_during_system2_analysis(monkeypatch):
    """Verify upstream audio chunks continue flowing non-blockingly while System 2 analyzes."""
    import app.services.reasoning_engine as reasoning_engine

    async def _test():
        monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", True)
        monkeypatch.setattr(reasoning_engine, "MOCK_REASONING_LATENCY_SEC", 0.15)

        manager = MockLiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()
        await manager._update_client_status(ws_mock, "listening")

        # Cross the 64KB trigger threshold to launch background System 2 evaluation
        manager._accumulate_candidate_audio(ws_mock, 64000)
        assert len(manager._background_tasks) == 1

        # Wait briefly for task to enter 'analyzing' state
        await asyncio.sleep(0.02)
        assert manager.state.client_status == "analyzing"

        # Stream additional audio while System 2 is still running
        manager._accumulate_candidate_audio(ws_mock, 6400)
        assert manager.state.upstream_bytes_during_analysis == 6400

        await manager._cancel_active_turn()

    asyncio.run(_test())


def test_system2_fallback_on_malformed_json_or_timeout(monkeypatch):
    """Verify reasoning_engine returns FALLBACK_EVALUATION on malformed JSON and timeout handoff payload on timeout."""
    import app.services.reasoning_engine as reasoning_engine
    from app.config import settings

    async def _test():
        monkeypatch.setattr(reasoning_engine, "USE_MOCK_AI", False)

        # 1. Malformed JSON -> FALLBACK_EVALUATION
        bad_resp = MagicMock()
        bad_resp.text = "{not-valid-json"
        fake_client = MagicMock()
        fake_client.aio.models.generate_content = AsyncMock(return_value=bad_resp)
        monkeypatch.setattr(reasoning_engine, "gemini_client", lambda: fake_client)

        result = await reasoning_engine.evaluate_candidate_approach(
            PROBLEMS["longest-palindrome"], "test approach"
        )
        assert result == reasoning_engine.FALLBACK_EVALUATION

        # 2. Timeout -> TIMEOUT_EVALUATION + self-answer FunctionResponse handoff
        async def _slow_generate(*_args, **_kwargs):
            await asyncio.sleep(0.5)

        fake_client.aio.models.generate_content = AsyncMock(side_effect=_slow_generate)
        monkeypatch.setattr(settings, "SYSTEM2_TIMEOUT_SEC", 0.05)

        manager = LiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()
        session_mock = MagicMock()
        session_mock.send_tool_response = AsyncMock()

        call = MagicMock()
        call.id = "call_timeout_1"
        call.name = "evaluate_approach"
        call.args = {"user_approach_summary": "Slow approach"}

        await manager._execute_tool_call_async(ws_mock, session_mock, call)
        session_mock.send_tool_response.assert_awaited_once()
        sent_responses = session_mock.send_tool_response.call_args.kwargs["function_responses"]
        assert len(sent_responses) == 1
        assert sent_responses[0].response == reasoning_engine.SYSTEM2_TIMEOUT_RESPONSE
        assert sent_responses[0].response["status"] == "timeout"

    asyncio.run(_test())


def test_gemini_live_final_rubric_grading_and_timeout_fallback(monkeypatch):
    """Verify end-of-session rubric grading via submit_final_grade (0 and 1+ prior tool calls) and timeout fallback."""
    from app.config import settings
    from app.services.live_manager import summarize_evaluations

    async def _test():
        # Case 1: 0 prior evaluate_approach calls -> Gemini Live submits holistic rubric grade
        manager = LiveSessionManager("longest-palindrome")
        ws_mock = AsyncMock()
        session_mock = MagicMock()

        async def _send_content_and_grade(**_kwargs):
            call = MagicMock()
            call.name = "submit_final_grade"
            call.args = {
                "final_complexity": "O(N^2) / O(1)",
                "is_optimal": False,
                "correctness_score": 8.0,
                "complexity_score": 7.5,
                "edge_cases_score": 6.5,
                "communication_score": 8.5,
                "overall_score": 7.6,
                "missed_edge_cases": ["All identical characters"],
                "summary_feedback": "Clear explanation with minimal fillers. Consider Manacher's algorithm for O(N).",
            }
            tc = MagicMock()
            tc.function_calls = [call]
            manager._dispatch_tool_call(ws_mock, session_mock, tc)

        session_mock.send_client_content = AsyncMock(side_effect=_send_content_and_grade)
        await manager._request_final_live_grade(session_mock)

        autopsy = summarize_evaluations(manager.state, manager.state.evaluations)
        assert autopsy.grading_source == "gemini_live"
        assert autopsy.score == 7.6
        assert autopsy.correctness_score == 8.0
        assert autopsy.complexity_score == 7.5
        assert autopsy.edge_cases_score == 6.5
        assert autopsy.communication_score == 8.5
        assert autopsy.final_complexity == "O(N^2) / O(1)"
        assert "minimal fillers" in autopsy.summary_feedback

        # Case 2: 1+ prior evaluations + Gemini Live final grade timeout -> falls back cleanly
        manager2 = LiveSessionManager("longest-palindrome")
        manager2.state.evaluations.append(
            Evaluation(
                time_complexity="O(N^3)",
                space_complexity="O(1)",
                is_optimal=False,
                issues=["Cubic time"],
                missed_edge_cases=["Even-length palindromes"],
                next_socratic_hint="Can you expand from a center?",
                score_delta=4.5,
            )
        )
        slow_session = MagicMock()
        slow_session.send_client_content = AsyncMock()
        monkeypatch.setattr(settings, "FINAL_GRADE_TIMEOUT_SEC", 0.05)

        await manager2._request_final_live_grade(slow_session)
        fallback_autopsy = summarize_evaluations(manager2.state, manager2.state.evaluations)
        assert fallback_autopsy.grading_source == "system2"
        assert fallback_autopsy.final_complexity == "O(N^3) / O(1)"
        assert fallback_autopsy.score == 4.5
        assert fallback_autopsy.communication_score > 0.0

    asyncio.run(_test())
