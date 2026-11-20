from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from uuid import uuid4

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_LIVE_MODEL,
    SESSION_MAX_DURATION_SEC,
    UPSTREAM_SAMPLE_RATE,
)
from app.data.problems import PROBLEMS
from app.models.schemas import Autopsy, Evaluation, Problem, SessionRow
from app.services.csv_storage import append_session
from app.services.reasoning_engine import evaluate_candidate_approach

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=GEMINI_API_KEY)

_EVALUATE_APPROACH_DECLARATION = types.FunctionDeclaration(
    name="evaluate_approach",
    description=(
        "Evaluate the candidate's proposed approach against the problem's "
        "constraints and optimal complexity. Call ONLY when the candidate "
        "proposes a concrete data structure, algorithm, or architectural "
        "component. Never call for greetings, clarifications, or pauses."
    ),
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "problem_id": types.Schema(
                type="STRING",
                description="The ID of the problem being discussed.",
            ),
            "user_approach_summary": types.Schema(
                type="STRING",
                description=(
                    "A concise 2-3 sentence summary of the candidate's "
                    "proposed approach, data structures, and algorithm."
                ),
            ),
        },
        required=["problem_id", "user_approach_summary"],
    ),
)


def _build_system_instruction(problem: Problem) -> str:
    return f"""\
You are a senior technical interviewer conducting a live voice interview. \
The candidate is practicing in an eyes-free, audio-only "pocket mode" \
during their commute.

## Current Problem
**{problem.title}** ({problem.category}, {problem.difficulty})
{problem.statement}

## Rules
1. Start by reading the problem statement clearly, then ask if the candidate \
has any clarifying questions.
2. Listen actively. Use brief verbal affirmations ("Got it", "Okay") while \
the candidate is speaking.
3. When the candidate proposes a concrete approach (data structure, algorithm, \
or architectural component), say a brief filler like "Let me trace that \
complexity real quick..." and immediately call `evaluate_approach`.
4. After receiving the evaluation result, deliver the `next_socratic_hint` \
naturally in your own voice — never read raw JSON to the candidate.
5. If `is_optimal` is true, congratulate briefly and probe edge cases.
6. NEVER evaluate Big-O complexity yourself. ALWAYS delegate to `evaluate_approach`.
7. NEVER be sycophantic. If the approach is suboptimal, say so with warmth but honesty.
8. Keep all spoken responses under 3 sentences to maintain conversational pace.
9. If the candidate goes silent for >10 seconds, gently prompt them.
10. When the session nears the time limit, guide toward a summary.\
"""


@dataclass
class LiveSession:
    session_id: str = field(default_factory=lambda: uuid4().hex[:12])
    problem_id: str = ""
    start_time: float = field(default_factory=time.time)
    evaluations: list[Evaluation] = field(default_factory=list)
    is_active: bool = True


class LiveSessionManager:
    """Bridges a client WebSocket to a Gemini Live API session with System 2 tool calls."""

    def __init__(self, problem_id: str) -> None:
        self.problem = PROBLEMS[problem_id]
        self.state = LiveSession(problem_id=problem_id)
        self._gemini_session: types.AsyncSession | None = None

    async def run(self, ws) -> Autopsy | None:  # noqa: ANN001 — WebSocket type varies
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Orus")
                )
            ),
            system_instruction=types.Content(
                parts=[types.Part(text=_build_system_instruction(self.problem))]
            ),
            tools=[types.Tool(function_declarations=[_EVALUATE_APPROACH_DECLARATION])],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        try:
            async with _client.aio.live.connect(
                model=GEMINI_LIVE_MODEL, config=config
            ) as session:
                self._gemini_session = session

                upstream_task = asyncio.create_task(
                    self._upstream_loop(ws, session)
                )
                downstream_task = asyncio.create_task(
                    self._downstream_loop(ws, session)
                )
                timeout_task = asyncio.create_task(
                    self._session_timer(ws, session)
                )

                done, pending = await asyncio.wait(
                    [upstream_task, downstream_task, timeout_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                for task in done:
                    if task.exception() and not isinstance(
                        task.exception(), asyncio.CancelledError
                    ):
                        logger.error(
                            "Task failed: %s", task.exception(), exc_info=True
                        )

        except Exception:
            logger.exception("Gemini Live session error")
        finally:
            self.state.is_active = False
            self._gemini_session = None

        return await self._build_autopsy(ws)

    async def _upstream_loop(self, ws, session: types.AsyncSession) -> None:
        try:
            async for message in ws.iter_data():
                if not self.state.is_active:
                    break

                if isinstance(message, bytes):
                    await session.send(
                        input=types.LiveClientRealtimeInput(
                            media_chunks=[
                                types.Blob(
                                    data=message,
                                    mime_type=f"audio/pcm;rate={UPSTREAM_SAMPLE_RATE}",
                                )
                            ]
                        )
                    )
                elif isinstance(message, str):
                    try:
                        control = json.loads(message)
                        if control.get("type") == "end_session":
                            self.state.is_active = False
                            return
                    except json.JSONDecodeError:
                        logger.warning("Ignoring malformed client control frame")
        except Exception:
            logger.info("Upstream loop ended (client disconnect)")

    async def _downstream_loop(self, ws, session: types.AsyncSession) -> None:
        try:
            async for response in session.receive():
                if not self.state.is_active:
                    break

                server_content = response.server_content
                tool_call = response.tool_call

                if server_content:
                    if server_content.interrupted:
                        await _send_json(ws, {"type": "clear_audio_buffer"})
                        await _send_json(
                            ws, {"type": "state", "status": "listening"}
                        )
                        continue

                    if server_content.model_turn and server_content.model_turn.parts:
                        for part in server_content.model_turn.parts:
                            if part.inline_data and part.inline_data.data:
                                await _send_json(
                                    ws, {"type": "state", "status": "speaking"}
                                )
                                await ws.send_bytes(part.inline_data.data)

                    if server_content.turn_complete:
                        await _send_json(
                            ws, {"type": "state", "status": "listening"}
                        )

                elif tool_call:
                    await self._handle_tool_call(ws, session, tool_call)

        except Exception:
            logger.info("Downstream loop ended")

    async def _handle_tool_call(
        self,
        ws,
        session: types.AsyncSession,
        tool_call: types.LiveServerToolCall,
    ) -> None:
        for fc in tool_call.function_calls:
            if fc.name != "evaluate_approach":
                continue

            await _send_json(ws, {"type": "state", "status": "analyzing"})

            args = fc.args or {}
            problem_id = args.get("problem_id", self.problem.id)
            summary = args.get("user_approach_summary", "")

            problem = PROBLEMS.get(problem_id, self.problem)
            evaluation = await evaluate_candidate_approach(problem, summary)
            self.state.evaluations.append(evaluation)

            await session.send(
                input=types.LiveClientToolResponse(
                    function_responses=[
                        types.FunctionResponse(
                            name="evaluate_approach",
                            id=fc.id,
                            response=evaluation.model_dump(),
                        )
                    ]
                )
            )

    async def _session_timer(self, ws, session: types.AsyncSession) -> None:
        await asyncio.sleep(SESSION_MAX_DURATION_SEC)
        logger.info("Session %s hit %ds hard cap", self.state.session_id, SESSION_MAX_DURATION_SEC)
        self.state.is_active = False

    async def _build_autopsy(self, ws) -> Autopsy | None:
        duration = int(time.time() - self.state.start_time)
        evals = self.state.evaluations

        if evals:
            last = evals[-1]
            final_complexity = f"T:{last.time_complexity} S:{last.space_complexity}"
            is_optimal = last.is_optimal
            score = min(10.0, sum(e.score_delta for e in evals))
            all_missed: list[str] = []
            for e in evals:
                all_missed.extend(e.missed_edge_cases)
            missed = list(dict.fromkeys(all_missed))  # dedupe, preserve order
            feedback = evals[-1].next_socratic_hint
        else:
            final_complexity = "Not evaluated"
            is_optimal = False
            score = 0.0
            missed = []
            feedback = "Session ended before any approach was evaluated."

        autopsy = Autopsy(
            session_id=self.state.session_id,
            problem_id=self.state.problem_id,
            duration_sec=duration,
            final_complexity=final_complexity,
            is_optimal=is_optimal,
            score=score,
            missed_edge_cases=missed,
            summary_feedback=feedback,
        )

        row = SessionRow(
            session_id=autopsy.session_id,
            timestamp_utc="",  # will be set by default_factory
            problem_id=autopsy.problem_id,
            duration_sec=autopsy.duration_sec,
            final_complexity=autopsy.final_complexity,
            is_optimal=autopsy.is_optimal,
            score=autopsy.score,
            missed_edge_cases="; ".join(autopsy.missed_edge_cases),
            summary_feedback=autopsy.summary_feedback,
        )
        row.timestamp_utc = SessionRow().timestamp_utc  # fresh timestamp
        await append_session(row)

        try:
            await _send_json(ws, {"type": "autopsy", **autopsy.model_dump()})
        except Exception:
            logger.warning("Could not send autopsy to client (already disconnected)")

        return autopsy


async def _send_json(ws, payload: dict) -> None:
    await ws.send_text(json.dumps(payload))
