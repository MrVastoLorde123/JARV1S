from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/work_planning.py": ["WorkPlan", "next_ready_steps"],
    "src/agency/task_orchestration.py": [
        "TaskOrchestration",
        "CoordinationDecision",
        "choose_next_coordination",
        "update_orchestration",
        "does not authorize",
    ],
    "src/agency/tests/test_task_orchestration.py": [
        "test_orchestration_preserves_plan_order_and_selects_first_ready_step",
        "test_completed_step_unlocks_dependent_step_deterministically",
        "test_active_blocked_and_failed_states_never_execute_actions",
        "test_all_completed_steps_produce_terminal_completion",
    ],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M33 task orchestration contract: FAIL {relative}: {missing}")

print("M33 task orchestration contract: PASS")
