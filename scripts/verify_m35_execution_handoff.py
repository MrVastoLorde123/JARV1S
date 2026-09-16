from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/execution_handoff.py": ["ExecutionHandoff", "create_execution_handoff", "ExecutionPreparationStatus.READY"],
    "src/agency/tests/test_execution_handoff.py": [
        "test_handoff_requires_ready_preparation_and_matching_request",
        "test_blocked_preparation_is_rejected_without_creating_authority",
        "test_handoff_does_not_expose_authorization_creation_or_execution",
    ],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M35 execution handoff contract: FAIL {relative}: {missing}")

print("M35 execution handoff contract: PASS")
