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
from app.models.schemas import Autopsy, Evaluation, Problem, SessionRow
from app.prompts import build_live_system_prompt
from app.services.csv_storage import append_session
from app.services.gemini_client import gemini_client
from app.services.reasoning_engine import evaluate_candidate_approach

logger = logging.getLogger(__name__)

_UPSTREAM_MIME = f"audio/pcm;rate={UPSTREAM_SAMPLE_RATE}"
_FINAL_TRANSCRIPT_CHARS = 1200

_DOWNSTREAM_CHUNK_SEC = 0.1
_DOWNSTREAM_CHUNK_BYTES = int(DOWNSTREAM_SAMPLE_RATE * _DOWNSTREAM_CHUNK_SEC) * 2
MOCK_TURN_TRIGGER_BYTES = UPSTREAM_SAMPLE_RATE * 2 * 2  # ~2s of 16kHz 16-bit mono

_EVALUATE_APPROACH_DECLARATION = types.FunctionDeclaration(
    name="evaluate_approach",
    description=(
        "Evaluate the candidate's proposed approach against the problem's "
        "constraints and optimal complexity. Call ONLY when the candidate "
        "proposes a concrete data structure, algorithm, or architectural "
        "component. Never call for greetings, clarifications, or pauses."
    ),
    parameters=types.Schema(
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
    candidate_transcript: list[str] = field(default_factory=list)
    client_status: str = ""


class SessionBridge:
    """Shared client-facing contract for real and mock interview sessions."""

    def __init__(self, problem_id: str) -> None:
        self.problem = PROBLEMS[problem_id]
        self.state = LiveSessionState(problem_id=problem_id)

    async def run(self, ws: WebSocket) -> Autopsy:
        raise NotImplementedError

    async def _update_client_status(self, ws: WebSocket, status: str) -> None:
        if status == self.state.client_status:
            return
        self.state.client_status = status
        await self._send_json(ws, {"type": "state", "status": status})

    async def _record_evaluation(self, ws: WebSocket, summary: str) -> Evaluation:
        await self._update_client_status(ws, "analyzing")
        await self._send_json(ws, {"type": "tool_call", "name": "evaluate_approach", "summary": summary})
        evaluation = await evaluate_candidate_approach(self.problem, summary)
        self.state.evaluations.append(evaluation)
        await self._send_json(ws, {"type": "tool_result", **evaluation.model_dump()})
        return evaluation

    async def _persist_and_send_autopsy(self, ws: WebSocket, evaluations: list[Evaluation]) -> Autopsy:
        autopsy = summarize_evaluations(self.state, evaluations)
        await append_session(SessionRow(
            session_id=autopsy.session_id,
            problem_id=autopsy.problem_id,
            duration_sec=autopsy.duration_sec,
            final_complexity=autopsy.final_complexity,
            is_optimal=autopsy.is_optimal,
            score=autopsy.score,
            missed_edge_cases="; ".join(autopsy.missed_edge_cases),
            summary_feedback=autopsy.summary_feedback,
        ))
        await self._send_json(ws, {"type": "autopsy", **autopsy.model_dump()})
        return autopsy

    @staticmethod
    async def _send_json(ws: WebSocket, payload: dict) -> None:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            logger.debug("Client socket closed; dropped %s frame", payload.get("type"))


class LiveSessionManager(SessionBridge):
    """Bridges a client WebSocket to a Gemini Live session with System 2 tool calls."""

    def _build_live_config(self) -> types.LiveConnectConfig:
        return types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=build_live_system_prompt(self.problem, settings.PROMPT_MODE),
            tools=[types.Tool(function_declarations=[_EVALUATE_APPROACH_DECLARATION])],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

    async def run(self, ws: WebSocket) -> Autopsy:
        try:
            async with gemini_client().aio.live.connect(model=GEMINI_LIVE_MODEL, config=self._build_live_config()) as session:
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
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            logger.exception("Gemini Live session error")
            await self._send_json(ws, {"type": "error", "message": "Live session unavailable"})

        evaluations = self.state.evaluations
        if not evaluations and self.state.candidate_transcript:
            # No tool call fired, so grade the raw transcript once
            transcript = "".join(self.state.candidate_transcript)[-_FINAL_TRANSCRIPT_CHARS:]
            evaluations = [await evaluate_candidate_approach(self.problem, f"Candidate said: {transcript}")]
        return await self._persist_and_send_autopsy(ws, evaluations)

    async def _relay_client_to_gemini(self, ws: WebSocket, session) -> None:
        while True:
            message = await ws.receive()
            if message["type"] == "websocket.disconnect":
                return
            if message.get("bytes"):
                await session.send_realtime_input(audio=types.Blob(data=message["bytes"], mime_type=_UPSTREAM_MIME))
            elif message.get("text") and _parse_control_type(message["text"]) == "end_session":
                return

    async def _relay_gemini_to_client(self, ws: WebSocket, session) -> None:
        await self._update_client_status(ws, "listening")
        # session.receive() ends after each model turn, so re-enter it per turn
        while True:
            async for response in session.receive():
                if response.tool_call:
                    await self._handle_tool_call(ws, session, response.tool_call)
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
                            await ws.send_bytes(part.inline_data.data)

                if content.turn_complete:
                    await self._update_client_status(ws, "listening")

    async def _handle_tool_call(self, ws: WebSocket, session, tool_call: types.LiveServerToolCall) -> None:
        responses: list[types.FunctionResponse] = []
        for call in tool_call.function_calls or []:
            if call.name != "evaluate_approach":
                continue
            evaluation = await self._record_evaluation(ws, (call.args or {}).get("user_approach_summary", ""))
            responses.append(types.FunctionResponse(id=call.id, name=call.name, response=evaluation.model_dump()))
        if responses:
            await session.send_tool_response(function_responses=responses)


class MockLiveSessionManager(SessionBridge):
    """Offline stand-in for Gemini Live that honours the exact same WebSocket contract."""

    def __init__(self, problem_id: str) -> None:
        super().__init__(problem_id)
        self._turn_task: asyncio.Task | None = None
        self._pending_candidate_bytes = 0

    async def run(self, ws: WebSocket) -> Autopsy:
        self._turn_task = asyncio.create_task(self._speak(ws, GREETING_CHIME_PCM))
        try:
            await asyncio.wait_for(self._relay_client_frames(ws), timeout=SESSION_MAX_DURATION_SEC)
        except asyncio.TimeoutError:
            logger.info("Mock session %s hit the %ds cap", self.state.session_id, SESSION_MAX_DURATION_SEC)
        finally:
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
        # Only count speech while idle, mirroring a real turn boundary
        if self.state.client_status != "listening":
            return
        self._pending_candidate_bytes += byte_count
        if self._pending_candidate_bytes >= MOCK_TURN_TRIGGER_BYTES:
            self._pending_candidate_bytes = 0
            self._turn_task = asyncio.create_task(self._run_mock_tool_call_turn(ws))

    async def _run_mock_tool_call_turn(self, ws: WebSocket) -> None:
        await self._record_evaluation(ws, f"Mock transcript: candidate proposed an approach for {self.problem.title}.")
        await self._speak(ws, HINT_CHIME_PCM)

    async def _speak(self, ws: WebSocket, pcm: bytes) -> None:
        await self._update_client_status(ws, "speaking")
        try:
            for offset in range(0, len(pcm), _DOWNSTREAM_CHUNK_BYTES):
                await ws.send_bytes(pcm[offset:offset + _DOWNSTREAM_CHUNK_BYTES])
                await asyncio.sleep(_DOWNSTREAM_CHUNK_SEC)  # Real-time pacing keeps AudioTrack's non-blocking buffer from dropping audio
        except Exception:
            logger.debug("Client socket closed mid-utterance")
            return
        await self._update_client_status(ws, "listening")

    async def _simulate_barge_in(self, ws: WebSocket) -> None:
        if self.state.client_status == "speaking":
            await self._cancel_active_turn()
        await self._send_json(ws, {"type": "clear_audio_buffer"})
        await self._update_client_status(ws, "listening")

    async def _cancel_active_turn(self) -> None:
        if self._turn_task and not self._turn_task.done():
            self._turn_task.cancel()
            await asyncio.gather(self._turn_task, return_exceptions=True)


def create_session_bridge(problem_id: str) -> SessionBridge:
    return MockLiveSessionManager(problem_id) if USE_MOCK_AI else LiveSessionManager(problem_id)


def summarize_evaluations(state: LiveSessionState, evaluations: list[Evaluation]) -> Autopsy:
    duration = int(time.time() - state.start_time)
    if not evaluations:
        return Autopsy(
            session_id=state.session_id, problem_id=state.problem_id, duration_sec=duration,
            final_complexity="Not evaluated", is_optimal=False, score=0.0, missed_edge_cases=[],
            summary_feedback="Session ended before any approach was proposed.",
        )
    latest = evaluations[-1]
    return Autopsy(
        session_id=state.session_id,
        problem_id=state.problem_id,
        duration_sec=duration,
        final_complexity=f"{latest.time_complexity} / {latest.space_complexity}",
        is_optimal=latest.is_optimal,
        score=round(min(10.0, max(e.score_delta for e in evaluations)), 1),
        missed_edge_cases=list(dict.fromkeys(case for e in evaluations for case in e.missed_edge_cases)),
        summary_feedback=latest.next_socratic_hint,
    )


def _parse_control_type(text: str) -> str:
    try:
        return str(json.loads(text).get("type", ""))
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Ignoring malformed client control frame")
        return ""
