from __future__ import annotations

import asyncio
import json
import logging

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_REASONING_MODEL, SYSTEM2_TIMEOUT_SEC
from app.models.schemas import Evaluation, Problem

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=GEMINI_API_KEY)

_SYSTEM2_PROMPT = """\
You are a rigorous algorithm and system design evaluator. You receive a problem \
statement with constraints and a candidate's proposed approach summary.

Evaluate the approach and return a JSON object with exactly these fields:
- time_complexity: string (Big-O notation)
- space_complexity: string (Big-O notation)
- is_optimal: boolean (true only if it matches or beats the optimal complexity)
- issues: list of strings (concrete flaws, TLE risks, correctness bugs)
- missed_edge_cases: list of strings (edge cases the candidate didn't address)
- next_socratic_hint: string (a single guiding question to nudge toward a better approach, \
  or encouragement if already optimal)
- score_delta: float 0-10 (how much this approach moves the candidate toward a perfect answer)

Be precise. Never be sycophantic. If the approach is wrong, say so directly.\
"""

_FALLBACK_EVALUATION = Evaluation(
    time_complexity="Unknown",
    space_complexity="Unknown",
    is_optimal=False,
    issues=["System 2 evaluation timed out or failed"],
    missed_edge_cases=[],
    next_socratic_hint="Let's continue — walk me through your approach step by step.",
    score_delta=0.0,
)


async def evaluate_candidate_approach(
    problem: Problem,
    user_approach_summary: str,
) -> Evaluation:
    prompt = (
        f"## Problem\n{problem.statement}\n\n"
        f"## Constraints\n" + "\n".join(f"- {c}" for c in problem.constraints) + "\n\n"
        f"## Optimal Target\n{problem.optimal_complexity}\n\n"
        f"## Candidate's Approach\n{user_approach_summary}"
    )
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                _client.models.generate_content,
                model=GEMINI_REASONING_MODEL,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=_SYSTEM2_PROMPT,
                    response_mime_type="application/json",
                    response_schema=Evaluation,
                    temperature=0.1,
                ),
            ),
            timeout=SYSTEM2_TIMEOUT_SEC,
        )
        parsed = json.loads(response.text)
        return Evaluation(**parsed)
    except asyncio.TimeoutError:
        logger.warning("System 2 timed out after %.1fs", SYSTEM2_TIMEOUT_SEC)
        return _FALLBACK_EVALUATION
    except Exception:
        logger.exception("System 2 evaluation failed")
        return _FALLBACK_EVALUATION
