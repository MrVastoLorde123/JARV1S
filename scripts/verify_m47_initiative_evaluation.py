"""Repository-local M47 initiative evaluation contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.initiative_candidate import InitiativeCandidate, InitiativeCandidateSet
from src.agency.initiative_evaluation import InitiativeEvaluation, build_initiative_evaluation_set

candidate_set = InitiativeCandidateSet(
    candidate_set_id="verify:candidates",
    reasoning_id="verify:reasoning",
    candidates=(
        InitiativeCandidate(
            "verify:candidate",
            "verify:reasoning",
            "Evaluate a bounded initiative.",
            rationale="Verification fixture.",
        ),
    ),
    unresolved_uncertainties=("value remains uncertain",),
)

evaluation = build_initiative_evaluation_set(
    candidate_set,
    evaluation_set_id="verify:evaluations",
    evaluations=(
        InitiativeEvaluation(
            "verify:candidate",
            "verify:candidates",
            0.75,
            0.70,
            0.60,
            "Descriptive evaluation only.",
            uncertainty_reasons=("value remains uncertain",),
        ),
    ),
)

payload = evaluation.to_context()
assert payload["candidate_set_id"] == candidate_set.candidate_set_id
assert payload["evaluation_count"] == 1
assert payload["truth_established"] is False
assert payload["intent_established"] is False
assert payload["authority_granted"] is False
assert payload["scheduling_requested"] is False
assert payload["notification_requested"] is False
assert payload["execution_requested"] is False
print("M47 initiative-evaluation contract: PASS")
