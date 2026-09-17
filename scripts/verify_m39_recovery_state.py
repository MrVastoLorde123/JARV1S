from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/recovery_state.py": [
        "RecoveryReconciliation",
        "RecoveryStateDisposition",
        "reconcile_recovery",
    ],
    "src/agency/tests/test_recovery_state.py": [
        "test_verified_recovery_closes_work_state",
        "test_rejected_recovery_reopens_planning_without_execution_authority",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M39 recovery state contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/recovery_state.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "provider", "subprocess", "tool_call"):
    if forbidden in text:
        raise SystemExit(f"M39 recovery state contract: FAIL forbidden authority/execution surface: {forbidden}")

print("M39 recovery state contract: PASS")
