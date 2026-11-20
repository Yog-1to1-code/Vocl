from app.data.problems import PROBLEMS
from app.prompts import build_live_system_prompt, build_reasoning_system_prompt


def test_build_live_system_prompt_prod():
    prob = PROBLEMS["longest-palindrome"]
    prompt = build_live_system_prompt(prob, mode="prod")

    assert "Staff Software Engineer" in prompt
    assert prob.title in prompt
    assert prob.statement in prompt
    assert f'problem_id="{prob.id}"' in prompt
    assert "Anti-sycophancy" in prompt
    assert "O of N squared" in prompt
    assert "ten to the five" in prompt
    assert "NON-BLOCKING TOOL-CALL & INTERRUPT PROTOCOL" in prompt
    assert "immediately interrupt politely" in prompt
    assert "Ready. State your approach." not in prompt


def test_build_live_system_prompt_test():
    prob = PROBLEMS["url-shortener"]
    prompt = build_live_system_prompt(prob, mode="test")

    # Test mode mirrors the full Staff Engineer persona plus an eager tool-call cue
    assert "Staff Software Engineer" in prompt
    assert prob.title in prompt
    assert f'problem_id="{prob.id}"' in prompt
    assert "NON-BLOCKING TOOL-CALL & INTERRUPT PROTOCOL" in prompt
    assert "Trigger evaluate_approach as soon as the candidate finishes their first concrete approach statement." in prompt
    assert "Ready. State your approach." not in prompt


def test_build_reasoning_system_prompt():
    prob = PROBLEMS["postgres-cpu-spike"]
    prompt = build_reasoning_system_prompt(prob)

    assert "Vocl's Deep Verification Engine (System 2)" in prompt
    assert prob.title in prompt
    assert prob.statement in prompt
    assert prob.optimal_complexity in prompt
    assert f"meet or beat `{prob.optimal_complexity}`" in prompt
    assert "Independently derive the true worst-case" in prompt
    assert "is_optimal" in prompt
    assert "score_delta" in prompt
    for edge_case in prob.key_edge_cases:
        assert edge_case in prompt
