from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/verification_recovery.py": ["RecoveryDecision", "RecoveryDisposition", "derive_recovery_decision"],
    "src/agency/tests/test_verification_recovery.py": ["test_verified_outcome_completes_objective_without_execution_authority", "test_rejected_verification_can_propose_bounded_continuation"],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M38 verification recovery contract: FAIL {relative}: {missing}")
print("M38 verification recovery contract: PASS")
