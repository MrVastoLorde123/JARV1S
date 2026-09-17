"""Repository-local M49 proactive proposal contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.information_gain import InformationGainAssessment, InformationGainOpportunity
from src.agency.initiative_evaluation import InitiativeEvaluation, InitiativeEvaluationSet
from src.agency.proactive_proposal import ProactiveProposal, build_proactive_proposal_set


evaluation_set = InitiativeEvaluationSet(
    "verify:eval:set",
    "verify:candidates",
    (
        InitiativeEvaluation(
            "verify:candidate",
            "verify:candidates",
            0.8,
            0.7,
            0.6,
            "bounded evaluation",
        ),
    ),
    ("verify:uncertainty",),
)

information_gain = InformationGainAssessment(
    "verify:ig",
    "verify:eval:set",
    (
        InformationGainOpportunity(
            "verify:opportunity",
            "verify:eval:set",
            "verify:uncertainty",
            0.75,
            "bounded uncertainty reduction",
            candidate_id="verify:candidate",
        ),
    ),
    ("verify:uncertainty",),
)

result = build_proactive_proposal_set(
    evaluation_set,
    information_gain,
    proposal_set_id="verify:proposals",
    proposals=(
        ProactiveProposal(
            "verify:proposal",
            "verify:eval:set",
            "Consider gathering the missing evidence.",
            "The proposed step could reduce a named uncertainty.",
            candidate_id="verify:candidate",
            information_gain_opportunity_ids=("verify:opportunity",),
            unresolved_uncertainties=("verify:uncertainty",),
        ),
    ),
)

payload = result.to_context()
assert payload["proposal_count"] == 1
assert payload["truth_established"] is False
assert payload["intent_established"] is False
assert payload["authority_granted"] is False
assert payload["scheduling_requested"] is False
assert payload["notification_requested"] is False
assert payload["authorization_requested"] is False
assert payload["execution_requested"] is False
print("M49 proactive-proposal contract: PASS")
