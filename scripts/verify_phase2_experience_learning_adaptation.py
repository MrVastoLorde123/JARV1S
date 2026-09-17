"""Static contract verifier for the complete Phase 2 learning loop."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ROOT / "src" / "agency" / "experience_feedback.py": "ExperienceFeedback",
    ROOT / "src" / "agency" / "experience_record.py": "ExperienceRecord",
    ROOT / "src" / "agency" / "learning_signal.py": "LearningSignal",
    ROOT / "src" / "agency" / "learning_evaluation.py": "LearningEvaluation",
    ROOT / "src" / "agency" / "adaptation_proposal.py": "AdaptationProposal",
    ROOT / "src" / "agency" / "adaptation_validation.py": "AdaptationValidation",
    ROOT / "src" / "agency" / "adaptation_application.py": "AdaptationApplication",
    ROOT / "src" / "agency" / "adaptation_outcome.py": "AdaptationOutcome",
}
forbidden = (
    "authorize(",
    "run_execution_handoff(",
    "execute(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess",
    "open(",
    "write_text(",
    "unlink(",
)

for target, marker in TARGETS.items():
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        raise SystemExit(f"Phase 2 contract: {target.name} missing {marker}")
    forbidden_found = [item for item in forbidden if item in text]
    if forbidden_found:
        raise SystemExit(f"Phase 2 contract: {target.name} contains forbidden surface {forbidden_found}")

print("Phase 2 experience-learning-adaptation contract: PASS")
