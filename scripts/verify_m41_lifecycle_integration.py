from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/lifecycle_integration.py": [
        "AgencyLifecycleIntegration",
        "build_agency_lifecycle_integration",
        "authorization_granted",
        "execution_requested",
    ],
    "src/agency/tests/test_lifecycle_integration.py": [
        "test_full_identity_chain_links_execution_verification_recovery_and_state",
        "test_identity_mismatch_fails_closed",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M41 lifecycle integration contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/lifecycle_integration.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "subprocess", "tool_call", "select_provider"):
    if forbidden in text:
        raise SystemExit(f"M41 lifecycle integration contract: FAIL forbidden authority/execution surface: {forbidden}")

print("M41 lifecycle integration contract: PASS")
