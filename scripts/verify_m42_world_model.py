from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/world_model.py": [
        "WorldModelFact",
        "WorldModelSnapshot",
        "build_world_model_snapshot",
        "truth_established",
        "authority_granted",
    ],
    "src/agency/tests/test_world_model.py": [
        "test_snapshot_preserves_observation_lineage",
        "test_fact_contract_rejects_invalid_lineage",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M42 world-model contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/world_model.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "subprocess", "tool_call", "select_provider"):
    if forbidden in text:
        raise SystemExit(f"M42 world-model contract: FAIL forbidden authority/execution surface: {forbidden}")

print("M42 world-model contract: PASS")
