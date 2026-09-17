from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/world_model_qualification.py": [
        "WorldFactAssessment",
        "WorldModelQualification",
        "assess_world_model",
        "truth_established",
        "authority_granted",
    ],
    "src/agency/tests/test_world_model_qualification.py": [
        "test_current_fact_is_usable_without_establishing_truth",
        "test_conflicting_peer_values_are_preserved_not_resolved",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M43 world-model qualification contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/world_model_qualification.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "subprocess", "tool_call", "select_provider", "truth ="):
    if forbidden in text:
        raise SystemExit(f"M43 world-model qualification contract: FAIL forbidden authority/truth surface: {forbidden}")

print("M43 world-model qualification contract: PASS")
