from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/lifecycle_state.py": [
        "AgencyLifecycleState",
        "build_agency_lifecycle_state",
        "authorization_granted",
        "execution_requested",
    ],
    "src/agency/tests/test_lifecycle_state.py": [
        "test_aggregate_requires_matching_identities",
        "test_recovery_can_be_attached_without_becoming_authority",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M40 lifecycle state contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/lifecycle_state.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "subprocess", "tool_call"):
    if forbidden in text:
        raise SystemExit(f"M40 lifecycle state contract: FAIL forbidden authority/execution surface: {forbidden}")

print("M40 lifecycle state contract: PASS")
