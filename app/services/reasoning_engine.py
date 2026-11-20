from __future__ import annotations

import asyncio
import logging

from google.genai import types
from pydantic import ValidationError

from app.config import GEMINI_REASONING_MODEL, MOCK_REASONING_LATENCY_SEC, SYSTEM2_TIMEOUT_SEC, USE_MOCK_AI
from app.models.schemas import Evaluation, Problem
from app.prompts import build_reasoning_system_prompt
from app.services.gemini_client import gemini_client

logger = logging.getLogger(__name__)

FALLBACK_EVALUATION = Evaluation(
    time_complexity="Unknown",
    space_complexity="Unknown",
    is_optimal=False,
    issues=["System 2 evaluation timed out or failed"],
    missed_edge_cases=[],
    next_socratic_hint="Let's continue. Walk me through your approach step by step.",
    score_delta=0.0,
)

MOCK_EVALUATIONS: dict[str, Evaluation] = {
    "longest-palindrome": Evaluation(
        time_complexity="O(N^3)",
        space_complexity="O(1)",
        is_optimal=False,
        issues=[
            "Enumerating all O(N^2) substrings and re-checking each one costs O(N) per check",
            "At N = 10^5 this is ~10^15 operations and will time out",
        ],
        missed_edge_cases=["Even-length palindromes like 'abba'", "All identical characters"],
        next_socratic_hint="When you check 'aba' and then 'xabax', what work are you repeating? Could you grow outward from a center instead?",
        score_delta=4.5,
    ),
    "url-shortener": Evaluation(
        time_complexity="O(1) read / O(1) write",
        space_complexity="O(N) keys",
        is_optimal=False,
        issues=[
            "Hashing the long URL and truncating to 7 chars invites collisions at 100M URLs/month",
            "No cache layer in front of the database for a 100:1 read-heavy workload",
        ],
        missed_edge_cases=["Hash collision resolution", "Hot-key thundering herd on viral links"],
        next_socratic_hint="If two long URLs hash to the same 7 characters, what happens? How could you hand out keys without ever colliding?",
        score_delta=5.5,
    ),
    "postgres-cpu-spike": Evaluation(
        time_complexity="Reactive restart",
        space_complexity="N/A",
        is_optimal=False,
        issues=[
            "Restarting the primary or scaling vCPUs hides the root cause instead of finding it",
            "No look at pg_stat_activity or pg_stat_statements before acting",
        ],
        missed_edge_cases=["Autovacuum blocked by long-running transactions", "Runaway analytics query without statement_timeout"],
        next_socratic_hint="Before you touch the instance, which system view would tell you exactly which queries are burning CPU right now?",
        score_delta=4.0,
    ),
}


def build_evaluation_prompt(problem: Problem, user_approach_summary: str) -> str:
    return f"Candidate proposed approach for problem '{problem.title}':\n{user_approach_summary}"


async def evaluate_candidate_approach(problem: Problem, user_approach_summary: str) -> Evaluation:
    if USE_MOCK_AI:
        await asyncio.sleep(MOCK_REASONING_LATENCY_SEC)
        return MOCK_EVALUATIONS.get(problem.id, FALLBACK_EVALUATION).model_copy(deep=True)

    config_kwargs: dict = {
        "system_instruction": build_reasoning_system_prompt(problem),
        "response_mime_type": "application/json",
        "response_schema": Evaluation,
        "temperature": 0.1,
        "max_output_tokens": 200,
    }
    # Use MINIMAL thinking on Gemini 3.x flash-lite (thinking_budget=0 returns 400 on 3.x)
    if "flash-lite" in GEMINI_REASONING_MODEL and hasattr(types, "ThinkingConfig"):
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="MINIMAL")

    try:
        response = await asyncio.wait_for(
            gemini_client().aio.models.generate_content(
                model=GEMINI_REASONING_MODEL,
                contents=build_evaluation_prompt(problem, user_approach_summary),
                config=types.GenerateContentConfig(**config_kwargs),
            ),
            timeout=SYSTEM2_TIMEOUT_SEC,
        )
        return Evaluation.model_validate_json(response.text)
    except asyncio.TimeoutError:
        logger.warning("System 2 timed out after %.1fs", SYSTEM2_TIMEOUT_SEC)
    except ValidationError:
        logger.exception("System 2 returned JSON that violates the Evaluation schema")
    except Exception:
        logger.exception("System 2 evaluation failed")
    return FALLBACK_EVALUATION
