"""Repository-local M46 initiative-candidate contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agency.current_context import CurrentContext, CurrentContextFact
from src.agency.initiative_candidate import InitiativeCandidate, build_initiative_candidate_set
from src.agency.reasoning import ReasoningHypothesis, build_reasoning_result
from src.agency.world_model import WorldModelFact
from src.agency.world_model_qualification import WorldFactQualification

context = CurrentContext(
    context_id="verify:m46:context",
    model_id="verify:m46:model",
    assessed_at="2026-09-16T21:00:00+00:00",
    facts=(
        CurrentContextFact(
            WorldModelFact(
                "verify:m46:fact",
                "verify:m46:subject",
                "verify:m46:domain",
                "usable",
                ("verify:m46:observation",),
            ),
            WorldFactQualification.USABLE,
        ),
    ),
)

reasoning = build_reasoning_result(
    context,
    reasoning_id="verify:m46:reasoning",
    hypotheses=(
        ReasoningHypothesis(
            "verify:m46:hypothesis",
            "A bounded hypothesis supports investigation.",
            0.75,
            supporting_fact_ids=("verify:m46:fact",),
            uncertainty_reasons=("requires downstream evaluation",),
        ),
    ),
    unresolved_uncertainties=("evaluation remains unresolved",),
)

result = build_initiative_candidate_set(
    reasoning,
    candidate_set_id="verify:m46:set",
    candidates=(
        InitiativeCandidate(
            "verify:m46:candidate",
            reasoning.reasoning_id,
            "Investigate the bounded condition.",
            supporting_hypothesis_ids=("verify:m46:hypothesis",),
        ),
    ),
)

payload = result.to_context()
assert payload["candidate_count"] == 1
assert payload["unresolved_uncertainties"] == reasoning.unresolved_uncertainties
assert payload["truth_established"] is False
assert payload["intent_established"] is False
assert payload["authority_granted"] is False
assert payload["scheduling_requested"] is False
assert payload["execution_requested"] is False
print("M46 initiative-candidate contract: PASS")
