from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/work_state.py": ["WorkState", "WorkRole", "infer_work_role"],
    "src/agency/work_planning.py": ["WorkPlan", "WorkPlanStep", "PlanStepKind", "next_ready_steps"],
    "src/agency/tests/test_work_planning.py": ["test_plan_is_anchored_to_work_state", "test_dependencies_define_deterministic_ready_steps", "test_planning_does_not_authorize_execution"],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"missing M32 planning marker {marker!r} in {relative}")

print("M32 work planning contract: PASS")
