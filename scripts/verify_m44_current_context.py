from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "src/agency/current_context.py": [
        "CurrentContextFact",
        "CurrentContext",
        "build_current_context",
        "truth_established",
        "intent_established",
        "execution_requested",
    ],
    "src/agency/tests/test_current_context.py": [
        "test_only_usable_facts_are_admitted",
        "test_non_usable_facts_are_excluded_not_resolved",
    ],
}
for relative, markers in REQUIRED.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M44 current-context contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/current_context.py").read_text(encoding="utf-8")
for forbidden in ("authorize(", "execute(", "subprocess", "tool_call", "select_provider", "truth ="):
    if forbidden in text:
        raise SystemExit(f"M44 current-context contract: FAIL forbidden authority/truth surface: {forbidden}")

print("M44 current-context contract: PASS")
