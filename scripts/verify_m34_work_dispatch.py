from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/work_dispatch.py": ["DispatchRequest", "DispatchResult", "WorkDispatcher", "authorization_granted", "execution_requested"],
    "src/agency/tests/test_work_dispatch.py": ["test_dispatch_binds_selected_step_to_bounded_assignment", "test_missing_capability_is_rejected_before_assignment", "test_dispatch_is_not_authorization_or_execution"],
    "src/agency/__init__.py": ["DispatchRequest", "DispatchResult", "WorkDispatcher"],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M34 work dispatch contract: FAIL {relative}: {missing}")

print("M34 work dispatch contract: PASS")
