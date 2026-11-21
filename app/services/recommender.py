"""Deterministic spaced-repetition commute recommender and streak calculator."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from app.db.models import SessionRecord
from app.models.schemas import Problem

_DIFFICULTY_RANK = {"Easy": 0, "Medium": 1, "Hard": 2}
_DIMENSION_LABELS = {
    "correctness": "Correctness",
    "complexity": "Complexity",
    "edge_cases": "Edge Cases",
    "communication": "Communication",
}
_STARTER_IDS = [
    ("two-sum", "Warm-up: crisp 5-minute hash map opener"),
    ("longest-palindrome", "Core drill: defend time vs. space trade-offs"),
    ("url-shortener", "Commute mix: high-yield system design classic"),
]


def _as_utc_date(dt: datetime) -> date:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).date()
    return dt.astimezone(timezone.utc).date()


def compute_streak_days(timestamps: list[datetime], today: date | None = None) -> int:
    """Count consecutive UTC days with at least one session ending today or yesterday."""
    if not timestamps:
        return 0
    active_days = {_as_utc_date(ts) for ts in timestamps}
    anchor = today or datetime.now(timezone.utc).date()
    if anchor not in active_days:
        yesterday = anchor - timedelta(days=1)
        if yesterday not in active_days:
            return 0
        anchor = yesterday

    streak = 0
    cursor = anchor
    while cursor in active_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _queue_item(problem: Problem, slot: str, reason: str) -> dict:
    return {
        "problem_id": problem.id,
        "title": problem.title,
        "category": problem.category,
        "difficulty": problem.difficulty,
        "duration_min": problem.duration_min,
        "slot": slot,
        "reason": reason,
    }


def _weakest_session_dimension(session: SessionRecord) -> tuple[str, float]:
    dims = {
        "correctness": float(session.correctness_score),
        "complexity": float(session.complexity_score),
        "edge_cases": float(session.edge_cases_score),
        "communication": float(session.communication_score),
    }
    weak_key = min(dims, key=lambda k: dims[k])
    return weak_key, dims[weak_key]


def build_commute_recommendations(
    problems: list[Problem],
    sessions: list[SessionRecord],
    now: datetime | None = None,
) -> dict:
    """Build a 3-drill spaced-repetition commute queue from the user's session history."""
    ref_now = now or datetime.now(timezone.utc)
    if ref_now.tzinfo is None:
        ref_now = ref_now.replace(tzinfo=timezone.utc)
    by_id = {p.id: p for p in problems}
    streak_days = compute_streak_days([s.created_at for s in sessions], today=ref_now.date())

    if not sessions:
        starter_queue: list[dict] = []
        for pid, reason in _STARTER_IDS:
            prob = by_id.get(pid)
            if prob is not None:
                starter_queue.append(_queue_item(prob, "starter", reason))
        return {
            "weakest_dimension": None,
            "dimension_averages": {
                "correctness": None,
                "complexity": None,
                "edge_cases": None,
                "communication": None,
            },
            "streak_days": 0,
            "queue": starter_queue,
        }

    count = len(sessions)
    dim_averages = {
        "correctness": round(sum(float(s.correctness_score) for s in sessions) / count, 2),
        "complexity": round(sum(float(s.complexity_score) for s in sessions) / count, 2),
        "edge_cases": round(sum(float(s.edge_cases_score) for s in sessions) / count, 2),
        "communication": round(sum(float(s.communication_score) for s in sessions) / count, 2),
    }
    weakest_dimension = min(dim_averages, key=lambda k: dim_averages[k])

    # Track per-problem latest/worst performance and category practice counts
    attempted_ids: set[str] = set()
    category_counts: dict[str, int] = defaultdict(int)
    retry_candidates: list[SessionRecord] = []
    for s in sessions:
        attempted_ids.add(s.problem_id)
        prob = by_id.get(s.problem_id)
        if prob is not None:
            category_counts[prob.category] += 1
        if float(s.overall_score) < 7.0 or not s.is_optimal:
            retry_candidates.append(s)

    queue: list[dict] = []
    chosen_ids: set[str] = set()

    # Slot 1: Weakness Targeting / Spaced Retry (prefer >= 1 day ago, else lowest score)
    if retry_candidates:
        cutoff = ref_now - timedelta(days=1)

        def _session_utc(s: SessionRecord) -> datetime:
            return s.created_at if s.created_at.tzinfo else s.created_at.replace(tzinfo=timezone.utc)

        spaced = [s for s in retry_candidates if _session_utc(s) <= cutoff]
        pool = spaced if spaced else retry_candidates
        target_session = min(pool, key=lambda s: (float(s.overall_score), float(getattr(s, f"{weakest_dimension}_score", 0.0))))
        target_prob = by_id.get(target_session.problem_id)
        if target_prob is not None:
            weak_key, weak_val = _weakest_session_dimension(target_session)
            if not target_session.is_optimal and float(target_session.overall_score) >= 7.0:
                reason = f"Retry: suboptimal complexity ({target_session.overall_score:.1f}/10)"
            else:
                reason = f"Retry: scored {weak_val:.0f}/10 on {_DIMENSION_LABELS[weak_key]}"
            queue.append(_queue_item(target_prob, "retry", reason))
            chosen_ids.add(target_prob.id)

    unattempted = [p for p in problems if p.id not in attempted_ids and p.id not in chosen_ids]

    # Slot 2: Next unseen drill in least-practiced category, Easy -> Medium -> Hard
    if unattempted:
        unseen_categories = sorted(
            {p.category for p in unattempted},
            key=lambda cat: (category_counts.get(cat, 0), 0 if cat == "DSA" else 1),
        )
        preferred_cat = unseen_categories[0]
        cat_pool = sorted(
            [p for p in unattempted if p.category == preferred_cat],
            key=lambda p: (_DIFFICULTY_RANK.get(p.difficulty, 1), p.duration_min),
        )
        next_prob = cat_pool[0]
        queue.append(
            _queue_item(
                next_prob,
                "next_unseen",
                f"Next {next_prob.difficulty} {next_prob.category} · sharpen {_DIMENSION_LABELS[weakest_dimension]}",
            )
        )
        chosen_ids.add(next_prob.id)

    # Slot 3: Quick Commute Mix (unattempted System Design or Debugging to balance DSA)
    mix_pool = [
        p for p in unattempted
        if p.id not in chosen_ids and p.category in ("System Design", "Debugging", "DevOps")
    ]
    if not mix_pool:
        mix_pool = [p for p in unattempted if p.id not in chosen_ids]
    if mix_pool:
        mix_pool.sort(key=lambda p: (category_counts.get(p.category, 0), _DIFFICULTY_RANK.get(p.difficulty, 1)))
        mix_prob = mix_pool[0]
        queue.append(
            _queue_item(
                mix_prob,
                "commute_mix",
                f"Commute mix: {mix_prob.duration_min}-min {mix_prob.category} drill",
            )
        )
        chosen_ids.add(mix_prob.id)

    # Backfill to 3 slots if user had no retry candidates
    if len(queue) < 3:
        for p in sorted(problems, key=lambda x: (_DIFFICULTY_RANK.get(x.difficulty, 1), x.duration_min)):
            if p.id not in chosen_ids:
                queue.append(_queue_item(p, "practice", f"Fresh {p.difficulty} {p.category} rep"))
                chosen_ids.add(p.id)
                if len(queue) >= 3:
                    break

    return {
        "weakest_dimension": weakest_dimension,
        "dimension_averages": dim_averages,
        "streak_days": streak_days,
        "queue": queue,
    }
