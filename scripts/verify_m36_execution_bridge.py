from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/execution_bridge.py": ["AgencyExecutionBridgeResult", "run_execution_handoff", "ControlledAgency"],
    "src/agency/tests/test_execution_bridge.py": [
        "test_bridge_runs_exact_ready_preparation_through_existing_agency",
        "test_bridge_preserves_authorization_boundary",
        "test_invalid_inputs_are_rejected",
    ],
    "src/agency/__init__.py": ["AgencyExecutionBridgeResult", "run_execution_handoff"],
}

for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M36 execution bridge contract: FAIL {relative}: {missing}")

print("M36 execution bridge contract: PASS")
