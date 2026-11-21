from __future__ import annotations

import asyncio
import json
import logging
import math
import sys
import time
from array import array
from dataclasses import dataclass, field
from uuid import uuid4

from fastapi import WebSocket
from google.genai import types

from app.config import (
    DOWNSTREAM_SAMPLE_RATE,
    GEMINI_LIVE_MODEL,
    PROMPT_MODE,
    SESSION_MAX_DURATION_SEC,
    UPSTREAM_SAMPLE_RATE,
    USE_MOCK_AI,
    settings,
)
from app.data.problems import PROBLEMS
from app.db.repository import record_session_and_increment_quota
from app.models.schemas import Autopsy, Evaluation, FinalRubricGrade, Problem
from app.prompts import build_final_grade_prompt, build_live_system_prompt
from app.services.gemini_client import gemini_client
from app.services.reasoning_engine import (
    SYSTEM2_TIMEOUT_RESPONSE,
    evaluate_candidate_approach,
    is_timeout_evaluation,
)
from app.services.session_recorder import SessionAudioRecorder

logger = logging.getLogger(__name__)

_UPSTREAM_MIME = f"audio/pcm;rate={UPSTREAM_SAMPLE_RATE}"
_FINAL_TRANSCRIPT_CHARS = 1200

_DOWNSTREAM_CHUNK_SEC = 0.1
_DOWNSTREAM_CHUNK_BYTES = int(DOWNSTREAM_SAMPLE_RATE * _DOWNSTREAM_CHUNK_SEC) * 2
MOCK_TURN_TRIGGER_BYTES = UPSTREAM_SAMPLE_RATE * 2 * 2  # ~2s of 16kHz 16-bit mono

_BEHAVIOR_NON_BLOCKING = getattr(getattr(types, "Behavior", None), "NON_BLOCKING", None)
_SCHEDULING_INTERRUPT = getattr(getattr(types, "FunctionResponseScheduling", None), "INTERRUPT", None)
# WHEN_IDLE delivers the verdict as soon as the candidate stops talking instead of cutting them off
_TOOL_RESPONSE_SCHEDULING = getattr(getattr(types, "FunctionResponseScheduling", None), "WHEN_IDLE", None) or _SCHEDULING_INTERRUPT

_declaration_kwargs = {
    "name": "evaluate_approach",
    "description": (
        "Evaluate the candidate's proposed approach against the problem's "
        "constraints and optimal complexity. Call ONLY when the candidate "
        "proposes a concrete data structure, algorithm, or architectural "
        "component. Never call for greetings, clarifications, or pauses."
    ),
    "parameters": types.Schema(
        type=types.Type.OBJECT,
        properties={
            "problem_id": types.Schema(type=types.Type.STRING, description="The ID of the problem being discussed."),
            "user_approach_summary": types.Schema(
                type=types.Type.STRING,
                description="A concise 2-3 sentence summary of the candidate's proposed approach.",
            ),
        },
        required=["problem_id", "user_approach_summary"],
    ),
}
if _BEHAVIOR_NON_BLOCKING is not None:
    _declaration_kwargs["behavior"] = _BEHAVIOR_NON_BLOCKING

_EVALUATE_APPROACH_DECLARATION = types.FunctionDeclaration(**_declaration_kwargs)

_SUBMIT_FINAL_GRADE_DECLARATION = types.FunctionDeclaration(
    name="submit_final_grade",
    description=(
        "Submit the final end-of-session rubric grade for the candidate across the full "
        "interview conversation. Call ONLY when explicitly told the session has ended."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "final_complexity": types.Schema(type=types.Type.STRING, description="Candidate's final time / space complexity, e.g. 'O(N^2) / O(1)'."),
            "is_optimal": types.Schema(type=types.Type.BOOLEAN, description="True only if the candidate reached the optimal complexity with sound logic."),
            "correctness_score": types.Schema(type=types.Type.NUMBER, description="0-10 score for problem & approach correctness."),
            "complexity_score": types.Schema(type=types.Type.NUMBER, description="0-10 score for complexity & scalability rigor."),
            "edge_cases_score": types.Schema(type=types.Type.NUMBER, description="0-10 score for edge cases & robustness."),
            "communication_score": types.Schema(type=types.Type.NUMBER, description="0-10 score for clarity, composure, pauses, and filler words."),
            "overall_score": types.Schema(type=types.Type.NUMBER, description="0-10 overall interview score."),
            "missed_edge_cases": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Up to 3 short phrases for missed edge cases.",
            ),
            "summary_feedback": types.Schema(type=types.Type.STRING, description="2 crisp coaching sentences covering technical rigor and delivery."),
        },
        required=[
            "final_complexity",
            "is_optimal",
            "correctness_score",
            "complexity_score",
            "edge_cases_score",
            "communication_score",
            "overall_score",
            "missed_edge_cases",
            "summary_feedback",
        ],
    ),
)


def _build_system_instruction(problem: Problem) -> str:
    return build_live_system_prompt(problem, settings.PROMPT_MODE)


def synthesize_chime_pcm(first_hz: float, second_hz: float, duration_sec: float = 1.0, amplitude: float = 0.22) -> bytes:
    note_samples = int(DOWNSTREAM_SAMPLE_RATE * duration_sec / 2)
    fade_samples = int(DOWNSTREAM_SAMPLE_RATE * 0.02)
    samples = array("h")
    for frequency_hz in (first_hz, second_hz):
        for i in range(note_samples):
            envelope = min(1.0, i / fade_samples, (note_samples - i) / fade_samples) * math.exp(-3.0 * i / note_samples)
            samples.append(int(32767 * amplitude * envelope * math.sin(2 * math.pi * frequency_hz * i / DOWNSTREAM_SAMPLE_RATE)))
    if sys.byteorder == "big":
        samples.byteswap()  # Wire format is little-endian PCM
    return samples.tobytes()


GREETING_CHIME_PCM = synthesize_chime_pcm(660.0, 880.0)
HINT_CHIME_PCM = synthesize_chime_pcm(880.0, 587.0)


@dataclass
class LiveSessionState:
    session_id: str = field(default_factory=lambda: uuid4().hex[:12])
    problem_id: str = ""
    start_time: float = field(default_factory=time.time)
    evaluations: list[Evaluation] = field(default_factory=list)
    final_grade: FinalRubricGrade | None = None
    candidate_transcript: list[str] = field(default_factory=list)
    client_status: str = ""
    upstream_bytes_received: int = 0
    upstream_bytes_during_analysis: int = 0
    audio_path: str | None = None
    events: list[dict] = field(default_factory=list)


class SessionBridge:
    """Shared client-facing contract for real and mock interview sessions."""

    def __init__(self, problem_id: str, user_id: str | None = None) -> None:
        self.problem = PROBLEMS[problem_id]
        self.user_id = user_id
        self.state = LiveSessionState(problem_id=problem_id)
        self._ws_write_lock = asyncio.Lock()
        self._closed = False

    async def run(self, ws: WebSocket) -> Autopsy:
        raise NotImplementedError

    def _log_event(self, event_type: str, latency_ms: float | None = None, payload: dict | None = None) -> None:
        self.state.events.append({
            "event_type": event_type,
            "latency_ms": round(latency_ms, 2) if latency_ms is not None else None,
            "payload": payload or {},
        })

    async def _update_client_status(self, ws: WebSocket, status: str) -> None:
        if self._closed or status == self.state.client_status:
            return
        self.state.client_status = status
        await self._send_json(ws, {"type": "state", "status": status})

    async def _record_evaluation(self, ws: WebSocket, summary: str) -> Evaluation:
        await self._update_client_status(ws, "analyzing")
        await self._send_json(ws, {"type": "tool_call", "name": "evaluate_approach", "summary": summary})
        self._log_event("tool_call", payload={"name": "evaluate_approach"})
        t0 = time.monotonic()
        evaluation = await evaluate_candidate_approach(self.problem, summary)
        elapsed_ms = (time.monotonic() - t0) * 1000.0
        self.state.evaluations.append(evaluation)
        event_kind = "timeout" if is_timeout_evaluation(evaluation) else "tool_result"
        self._log_event(
            event_kind,
            latency_ms=elapsed_ms,
            payload={"time_complexity": evaluation.time_complexity, "is_optimal": evaluation.is_optimal},
        )
        await self._send_json(ws, {"type": "tool_result", **evaluation.model_dump()})
        return evaluation

    async def _persist_and_send_autopsy(self, ws: WebSocket, evaluations: list[Evaluation]) -> Autopsy:
        autopsy = summarize_evaluations(self.state, evaluations)
        self._log_event("ws_close", payload={"duration_sec": autopsy.duration_sec, "grading_source": autopsy.grading_source})
        if self.user_id:
            await record_session_and_increment_quota(
                self.user_id,
                autopsy,
                audio_path=self.state.audio_path,
                events=self.state.events,
            )
        await self._send_json(ws, {"type": "autopsy", **autopsy.model_dump()}, allow_when_closing=True)
        return autopsy

    async def _send_json(self, ws: WebSocket, payload: dict, allow_when_closing: bool = False) -> None:
        if self._closed and not allow_when_closing:
            return
        async with self._ws_write_lock:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                logger.debug("Client socket closed; dropped %s frame", payload.get("type"))

    async def _send_bytes(self, ws: WebSocket, data: bytes) -> bool:
        if self._closed:
            return False
        async with self._ws_write_lock:
            try:
                await ws.send_bytes(data)
                return True
            except Exception:
                logger.debug("Client socket closed; dropped binary audio frame")
                return False


class LiveSessionManager(SessionBridge):
    """Bridges a client WebSocket to a Gemini Live session with System 2 tool calls."""

    def __init__(self, problem_id: str, user_id: str | None = None) -> None:
        super().__init__(problem_id, user_id=user_id)
        self._background_tasks: set[asyncio.Task] = set()
        self._tool_call_in_flight: bool = False
        self._last_tool_call_timestamp: float = 0.0
        self._grading_final: bool = False
        self._final_grade_ready = asyncio.Event()
        self._recorder: SessionAudioRecorder | None = (
            SessionAudioRecorder(self.state.session_id) if settings.RECORD_SESSIONS else None
        )

    def _build_live_config(self) -> types.LiveConnectConfig:
        return types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=build_live_system_prompt(self.problem, settings.PROMPT_MODE),
            tools=[types.Tool(function_declarations=[_EVALUATE_APPROACH_DECLARATION, _SUBMIT_FINAL_GRADE_DECLARATION])],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            # 500ms VAD triggers immediate turn handoff without post-speech dead air
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    silence_duration_ms=500,
                    end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                )
            ),
        )

    async def run(self, ws: WebSocket) -> Autopsy:
        try:
            async with gemini_client().aio.live.connect(model=GEMINI_LIVE_MODEL, config=self._build_live_config()) as session:
                await session.send_client_content(
                    turns=types.Content(role="user", parts=[types.Part(text="Begin the interview.")]),
                    turn_complete=True,
                )
                tasks = [
                    asyncio.create_task(self._relay_client_to_gemini(ws, session)),
                    asyncio.create_task(self._relay_gemini_to_client(ws, session)),
                    asyncio.create_task(asyncio.sleep(SESSION_MAX_DURATION_SEC)),
                ]
                try:
                    done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        if not task.cancelled() and task.exception():
                            logger.error("Session task failed", exc_info=task.exception())
                finally:
                    self._closed = True
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    for bg_task in list(self._background_tasks):
                        bg_task.cancel()
                    if self._background_tasks:
                        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        except Exception:
            self._closed = True
            logger.exception("Gemini Live session error")
            await self._send_json(ws, {"type": "error", "message": "Live session unavailable"}, allow_when_closing=True)

        if self._recorder is not None:
            try:
                saved = self._recorder.save_stereo_wav()
                if saved is not None:
                    self.state.audio_path = str(saved)
            except Exception:
                logger.exception("Failed to save session audio mix")

        evaluations = self.state.evaluations
        if self.state.final_grade is None and not evaluations and self.state.candidate_transcript:
            # Fallback when live final grading did not return and no tool call fired
            transcript = "".join(self.state.candidate_transcript)[-_FINAL_TRANSCRIPT_CHARS:]
            evaluations = [await evaluate_candidate_approach(self.problem, f"Candidate said: {transcript}")]
        return await self._persist_and_send_autopsy(ws, evaluations)

    async def _request_final_live_grade(self, session) -> None:
        """Ask the active Gemini Live session for a rubric evaluation before teardown."""
        self._grading_final = True
        prior = (
            f"{self.state.evaluations[-1].time_complexity} / {self.state.evaluations[-1].space_complexity}"
            if self.state.evaluations
            else None
        )
        t0 = time.monotonic()
        try:
            await session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part(text=build_final_grade_prompt(self.problem, prior))],
                ),
                turn_complete=True,
            )
            await asyncio.wait_for(self._final_grade_ready.wait(), timeout=settings.FINAL_GRADE_TIMEOUT_SEC)
            self._log_event("final_grade", latency_ms=(time.monotonic() - t0) * 1000.0, payload={"source": "gemini_live"})
        except asyncio.TimeoutError:
            self._log_event("timeout", latency_ms=(time.monotonic() - t0) * 1000.0, payload={"stage": "final_grade"})
            logger.warning("Gemini Live final rubric grade timed out after %.1fs; using fallback", settings.FINAL_GRADE_TIMEOUT_SEC)
        except Exception:
            logger.warning("Gemini Live final rubric grade failed; using fallback", exc_info=True)

    async def _relay_client_to_gemini(self, ws: WebSocket, session) -> None:
        while True:
            message = await ws.receive()
            if message["type"] == "websocket.disconnect":
                return
            if message.get("bytes"):
                if self._grading_final:
                    continue
                raw_pcm = message["bytes"]
                byte_len = len(raw_pcm)
                self.state.upstream_bytes_received += byte_len
                if self.state.client_status == "analyzing":
                    self.state.upstream_bytes_during_analysis += byte_len
                if self._recorder is not None:
                    self._recorder.record_user_pcm(raw_pcm)
                await session.send_realtime_input(audio=types.Blob(data=raw_pcm, mime_type=_UPSTREAM_MIME))
            elif message.get("text") and _parse_control_type(message["text"]) == "end_session":
                await self._request_final_live_grade(session)
                return

    async def _relay_gemini_to_client(self, ws: WebSocket, session) -> None:
        await self._update_client_status(ws, "listening")
        # session.receive() ends after each model turn, so re-enter it per turn
        while not self._closed:
            async for response in session.receive():
                if self._closed:
                    return
                if response.tool_call:
                    self._dispatch_tool_call(ws, session, response.tool_call)
                    continue

                if self._grading_final:
                    continue

                content = response.server_content
                if not content:
                    continue

                if content.interrupted:
                    await self._send_json(ws, {"type": "clear_audio_buffer"})
                    await self._update_client_status(ws, "listening")

                if content.input_transcription and content.input_transcription.text:
                    self.state.candidate_transcript.append(content.input_transcription.text)

                if content.model_turn and content.model_turn.parts:
                    for part in content.model_turn.parts:
                        if part.inline_data and part.inline_data.data:
                            await self._update_client_status(ws, "speaking")
                            if self._recorder is not None:
                                self._recorder.record_ai_pcm(part.inline_data.data)
                            if not await self._send_bytes(ws, part.inline_data.data):
                                return

                if content.turn_complete:
                    await self._update_client_status(ws, "listening")

    def _dispatch_tool_call(self, ws: WebSocket, session, tool_call: types.LiveServerToolCall) -> None:
        if self._closed:
            return
        for call in tool_call.function_calls or []:
            if call.name == "submit_final_grade":
                self._capture_final_grade(call.args or {})
                continue
            if call.name != "evaluate_approach" or self._grading_final:
                continue
            now = time.time()
            if self._tool_call_in_flight or (now - self._last_tool_call_timestamp < 3.0):
                logger.info("Ignoring duplicate/concurrent evaluate_approach call (in_flight=%s)", self._tool_call_in_flight)
                continue
            self._tool_call_in_flight = True
            self._last_tool_call_timestamp = now
            task = asyncio.create_task(self._execute_tool_call_async(ws, session, call))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    def _capture_final_grade(self, args: dict) -> None:
        try:
            self.state.final_grade = FinalRubricGrade.model_validate(args)
            self._final_grade_ready.set()
            logger.info("Captured Gemini Live final rubric grade: score=%.1f", self.state.final_grade.overall_score)
        except Exception:
            logger.warning("Malformed submit_final_grade args; falling back", exc_info=True)

    async def _execute_tool_call_async(self, ws: WebSocket, session, call) -> None:
        try:
            summary = (call.args or {}).get("user_approach_summary", "")
            evaluation = await self._record_evaluation(ws, summary)
            if self._closed:
                return
            response_payload = (
                SYSTEM2_TIMEOUT_RESPONSE
                if is_timeout_evaluation(evaluation)
                else evaluation.model_dump()
            )
            resp_kwargs = {
                "id": call.id,
                "name": call.name,
                "response": response_payload,
            }
            if _TOOL_RESPONSE_SCHEDULING is not None:
                resp_kwargs["scheduling"] = _TOOL_RESPONSE_SCHEDULING
            response = types.FunctionResponse(**resp_kwargs)
            await session.send_tool_response(function_responses=[response])
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Error executing asynchronous evaluate_approach tool call")
        finally:
            self._tool_call_in_flight = False


class MockLiveSessionManager(SessionBridge):
    """Offline stand-in for Gemini Live that honours the exact same WebSocket contract."""

    def __init__(self, problem_id: str, user_id: str | None = None) -> None:
        super().__init__(problem_id, user_id=user_id)
        self._turn_task: asyncio.Task | None = None
        self._background_tasks: set[asyncio.Task] = set()
        self._pending_candidate_bytes = 0
        self._tool_call_in_flight: bool = False
        self._last_tool_call_timestamp: float = 0.0

    async def run(self, ws: WebSocket) -> Autopsy:
        self._turn_task = asyncio.create_task(self._speak(ws, GREETING_CHIME_PCM))
        try:
            await asyncio.wait_for(self._relay_client_frames(ws), timeout=SESSION_MAX_DURATION_SEC)
        except asyncio.TimeoutError:
            logger.info("Mock session %s hit the %ds cap", self.state.session_id, SESSION_MAX_DURATION_SEC)
        finally:
            self._closed = True
            await self._cancel_active_turn()
        return await self._persist_and_send_autopsy(ws, self.state.evaluations)

    async def _relay_client_frames(self, ws: WebSocket) -> None:
        while True:
            message = await ws.receive()
            if message["type"] == "websocket.disconnect":
                return
            if message.get("bytes"):
                self._accumulate_candidate_audio(ws, len(message["bytes"]))
                continue
            control_type = _parse_control_type(message.get("text") or "")
            if control_type == "end_session":
                return
            if control_type == "simulate_barge_in":
                await self._simulate_barge_in(ws)

    def _accumulate_candidate_audio(self, ws: WebSocket, byte_count: int) -> None:
        self.state.upstream_bytes_received += byte_count
        if self.state.client_status == "analyzing":
            self.state.upstream_bytes_during_analysis += byte_count
            return
        # Only accumulate turn trigger threshold while listening
        if self.state.client_status != "listening":
            return
        self._pending_candidate_bytes += byte_count
        if self._pending_candidate_bytes >= MOCK_TURN_TRIGGER_BYTES:
            now = time.time()
            if self._tool_call_in_flight or (now - self._last_tool_call_timestamp < 3.0):
                return
            self._tool_call_in_flight = True
            self._last_tool_call_timestamp = now
            self._pending_candidate_bytes = 0
            task = asyncio.create_task(self._run_mock_tool_call_turn(ws))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def _run_mock_tool_call_turn(self, ws: WebSocket) -> None:
        try:
            await self._record_evaluation(ws, f"Mock transcript: candidate proposed an approach for {self.problem.title}.")
            if self._closed:
                return
            self._turn_task = asyncio.create_task(self._speak(ws, HINT_CHIME_PCM))
            await self._turn_task
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.debug("Mock turn cancelled or interrupted")
        finally:
            self._tool_call_in_flight = False

    async def _speak(self, ws: WebSocket, pcm: bytes) -> None:
        await self._update_client_status(ws, "speaking")
        for offset in range(0, len(pcm), _DOWNSTREAM_CHUNK_BYTES):
            if self._closed:
                return
            if not await self._send_bytes(ws, pcm[offset:offset + _DOWNSTREAM_CHUNK_BYTES]):
                return
            await asyncio.sleep(_DOWNSTREAM_CHUNK_SEC)  # Real-time pacing keeps AudioTrack's non-blocking buffer from dropping audio
        await self._update_client_status(ws, "listening")

    async def _simulate_barge_in(self, ws: WebSocket) -> None:
        if self.state.client_status == "speaking":
            await self._cancel_speech_turn()
        await self._send_json(ws, {"type": "clear_audio_buffer"})
        if not self._tool_call_in_flight:
            await self._update_client_status(ws, "listening")

    async def _cancel_speech_turn(self) -> None:
        if self._turn_task and not self._turn_task.done():
            self._turn_task.cancel()
            await asyncio.gather(self._turn_task, return_exceptions=True)

    async def _cancel_active_turn(self) -> None:
        await self._cancel_speech_turn()
        for bg in list(self._background_tasks):
            if not bg.done():
                bg.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)


def create_session_bridge(problem_id: str, user_id: str | None = None) -> SessionBridge:
    return (
        MockLiveSessionManager(problem_id, user_id=user_id)
        if USE_MOCK_AI
        else LiveSessionManager(problem_id, user_id=user_id)
    )


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(10.0, float(value))), 1)


def summarize_evaluations(state: LiveSessionState, evaluations: list[Evaluation]) -> Autopsy:
    duration = int(time.time() - state.start_time)
    if state.final_grade is not None:
        grade = state.final_grade
        return Autopsy(
            session_id=state.session_id,
            problem_id=state.problem_id,
            duration_sec=duration,
            final_complexity=grade.final_complexity,
            is_optimal=grade.is_optimal,
            score=_clamp_score(grade.overall_score),
            correctness_score=_clamp_score(grade.correctness_score),
            complexity_score=_clamp_score(grade.complexity_score),
            edge_cases_score=_clamp_score(grade.edge_cases_score),
            communication_score=_clamp_score(grade.communication_score),
            grading_source="gemini_live",
            missed_edge_cases=list(dict.fromkeys(grade.missed_edge_cases)),
            summary_feedback=grade.summary_feedback or "Session evaluated by Gemini Live.",
        )

    if not evaluations:
        return Autopsy(
            session_id=state.session_id, problem_id=state.problem_id, duration_sec=duration,
            final_complexity="Not evaluated", is_optimal=False, score=0.0,
            correctness_score=0.0, complexity_score=0.0, edge_cases_score=0.0, communication_score=0.0,
            grading_source="fallback", missed_edge_cases=[],
            summary_feedback="Session ended before any approach was proposed.",
        )

    latest = evaluations[-1]
    score = _clamp_score(max(e.score_delta for e in evaluations))
    missed = list(dict.fromkeys(case for e in evaluations for case in e.missed_edge_cases))
    return Autopsy(
        session_id=state.session_id,
        problem_id=state.problem_id,
        duration_sec=duration,
        final_complexity=f"{latest.time_complexity} / {latest.space_complexity}",
        is_optimal=latest.is_optimal,
        score=score,
        correctness_score=score,
        complexity_score=_clamp_score(8.5 if latest.is_optimal else max(2.5, score - 0.5)),
        edge_cases_score=_clamp_score(max(2.0, 10.0 - len(missed) * 2.0)),
        communication_score=_clamp_score(min(10.0, score + 1.0)),
        grading_source="system2",
        missed_edge_cases=missed,
        summary_feedback=latest.next_socratic_hint,
    )


def _parse_control_type(text: str) -> str:
    try:
        return str(json.loads(text).get("type", ""))
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Ignoring malformed client control frame")
        return ""
