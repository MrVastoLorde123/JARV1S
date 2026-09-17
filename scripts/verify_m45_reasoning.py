"""Repository-local M45 reasoning contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.current_context import CurrentContext, CurrentContextFact
from src.agency.reasoning import ReasoningHypothesis, build_reasoning_result
from src.agency.world_model import WorldModelFact
from src.agency.world_model_qualification import WorldFactQualification


context = CurrentContext(
    context_id="verify:context",
    model_id="verify:model",
    assessed_at="2026-09-16T21:00:00+00:00",
    facts=(
        CurrentContextFact(
            WorldModelFact(
                "verify:fact",
                "verify:subject",
                "verify:domain",
                "usable",
                ("verify:observation",),
            ),
            WorldFactQualification.USABLE,
        ),
    ),
)

result = build_reasoning_result(
    context,
    reasoning_id="verify:reasoning",
    hypotheses=(
        ReasoningHypothesis(
            "verify:hypothesis",
            "A bounded hypothesis is represented without declaring truth.",
            0.75,
            supporting_fact_ids=("verify:fact",),
            uncertainty_reasons=("requires downstream validation",),
        ),
    ),
    unresolved_uncertainties=("validation remains unresolved",),
)

payload = result.to_context()
assert payload["context_id"] == context.context_id
assert payload["hypothesis_count"] == 1
assert payload["truth_established"] is False
assert payload["authority_granted"] is False
assert payload["intent_established"] is False
assert payload["execution_requested"] is False
print("M45 reasoning-uncertainty contract: PASS")
