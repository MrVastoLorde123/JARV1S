from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/execution_outcome.py": [
        "AgencyExecutionOutcome",
        "VerificationInput",
        "VerificationDecision",
        "classify_agency_outcome",
    ],
    "src/agency/tests/test_execution_outcome.py": [
        "test_execution_observation_is_classified_without_claiming_verification",
        "test_verification_input_is_bounded_and_requires_external_decision",
        "test_verified_requires_evidence_and_invalid_inputs_are_rejected",
    ],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M37 execution outcome contract: FAIL {relative}: {missing}")

print("M37 execution outcome contract: PASS")
