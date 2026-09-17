"""Static contract verifier for the complete Phase 2 learning loop."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "src" / "agency" / "experience_feedback.py",
    ROOT / "src" / "agency" / "experience_record.py",
    ROOT / "src" / "agency" / "learning_signal.py",
    ROOT / "src" / "agency" / "learning_evaluation.py",
    ROOT / "src" / "agency" / "adaptation_proposal.py",
    ROOT / "src" / "agency" / "adaptation_validation.py",
    ROOT / "src" / "agency" / "adaptation_application.py",
    ROOT / "src" / "agency" / "adaptation_outcome.py",
)
required = (
    "ExperienceFeedback",
    "ExperienceRecord",
    "LearningSignal",
    "LearningEvaluation",
    "AdaptationProposal",
    "AdaptationValidation",
    "AdaptationApplication",
    "AdaptationOutcome",
)
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

for target in TARGETS:
    text = target.read_text(encoding="utf-8")
    missing = [marker for marker in required if marker in target.name and marker not in text]
    forbidden_found = [marker for marker in forbidden if marker in text]
    if missing:
        raise SystemExit(f"Phase 2 contract: {target.name} missing {missing}")
    if forbidden_found:
        raise SystemExit(f"Phase 2 contract: {target.name} contains forbidden surface {forbidden_found}")

print("Phase 2 experience-learning-adaptation contract: PASS")
