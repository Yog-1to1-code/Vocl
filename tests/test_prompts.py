from app.data.problems import PROBLEMS
from app.prompts import build_live_system_prompt, build_reasoning_system_prompt


def test_build_live_system_prompt_prod():
    prob = PROBLEMS["longest-palindrome"]
    prompt = build_live_system_prompt(prob, mode="prod")

    assert "Staff Software Engineer" in prompt
    assert prob.title in prompt
    assert prob.statement in prompt
    assert "evaluate_approach" in prompt
    assert f'problem_id="{prob.id}"' in prompt
    assert "Anti-sycophancy" in prompt
    assert "O of N squared" in prompt


def test_build_live_system_prompt_test():
    prob = PROBLEMS["url-shortener"]
    prompt = build_live_system_prompt(prob, mode="test")

    assert "fast verification mode" in prompt
    assert prob.title in prompt
    assert f"ID: {prob.id}" in prompt
    assert "Ready. State your approach." in prompt
    assert "evaluate_approach" in prompt


def test_build_reasoning_system_prompt():
    prob = PROBLEMS["postgres-cpu-spike"]
    prompt = build_reasoning_system_prompt(prob)

    assert "Vocl's Deep Verification Engine (System 2)" in prompt
    assert prob.title in prompt
    assert prob.statement in prompt
    assert prob.optimal_complexity in prompt
    assert "is_optimal" in prompt
    assert "score_delta" in prompt
    for edge_case in prob.key_edge_cases:
        assert edge_case in prompt
