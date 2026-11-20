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
    assert "native-audio" in GEMINI_LIVE_MODEL or "gemini" in GEMINI_LIVE_MODEL
    assert "gemini" in GEMINI_REASONING_MODEL
    assert SESSION_MAX_DURATION_SEC == 900
    assert SYSTEM2_TIMEOUT_SEC > 0


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
    assert config.tools[0].function_declarations[0].name == "evaluate_approach"
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
