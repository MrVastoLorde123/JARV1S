"""Repository-local M48 information-gain contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.information_gain import InformationGainOpportunity, build_information_gain_assessment
from src.agency.initiative_evaluation import InitiativeEvaluation, InitiativeEvaluationSet


evaluation_set = InitiativeEvaluationSet(
    "verify:evaluation-set",
    "verify:candidate-set",
    evaluations=(
        InitiativeEvaluation(
            "verify:candidate",
            "verify:candidate-set",
            0.8,
            0.7,
            0.6,
            "bounded evaluation",
        ),
    ),
    unresolved_uncertainties=("verify:uncertainty",),
)

assessment = build_information_gain_assessment(
    evaluation_set,
    assessment_id="verify:assessment",
    opportunities=(
        InformationGainOpportunity(
            "verify:opportunity",
            "verify:evaluation-set",
            "verify:uncertainty",
            0.8,
            "verification may reduce the named uncertainty",
            "verify:candidate",
        ),
    ),
)

payload = assessment.to_context()
assert payload["evaluation_set_id"] == evaluation_set.evaluation_set_id
assert payload["opportunity_count"] == 1
assert payload["unresolved_uncertainties"] == evaluation_set.unresolved_uncertainties
assert payload["truth_established"] is False
assert payload["intent_established"] is False
assert payload["authority_granted"] is False
assert payload["scheduling_requested"] is False
assert payload["execution_requested"] is False
print("M48 information-gain contract: PASS")
