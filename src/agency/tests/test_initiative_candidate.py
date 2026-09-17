from unittest import TestCase

from src.agency.initiative_candidate import (
    InitiativeCandidate,
    build_initiative_candidate_set,
)
from src.agency.reasoning import ReasoningHypothesis, build_reasoning_result
from src.agency.current_context import CurrentContext, CurrentContextFact
from src.agency.world_model import WorldModelFact
from src.agency.world_model_qualification import WorldFactQualification


class M46InitiativeCandidateTests(TestCase):
    def _reasoning(self):
        context = CurrentContext(
            context_id="m46:context",
            model_id="m46:model",
            assessed_at="2026-09-16T21:00:00+00:00",
            facts=(
                CurrentContextFact(
                    WorldModelFact(
                        "m46:fact", "m46:subject", "m46:domain", "observed", ("m46:obs",)
                    ),
                    WorldFactQualification.USABLE,
                ),
            ),
        )
        return build_reasoning_result(
            context,
            reasoning_id="m46:reasoning",
            hypotheses=(
                ReasoningHypothesis(
                    "m46:hypothesis",
                    "A bounded hypothesis.",
                    0.7,
                    supporting_fact_ids=("m46:fact",),
                    uncertainty_reasons=("needs validation",),
                ),
            ),
            unresolved_uncertainties=("validation remains unresolved",),
        )

    def test_candidate_must_reference_supplied_reasoning(self):
        reasoning = self._reasoning()
        candidate = InitiativeCandidate(
            "m46:candidate",
            "other:reasoning",
            "Investigate the observed condition.",
            supporting_hypothesis_ids=("m46:hypothesis",),
        )
        with self.assertRaises(ValueError):
            build_initiative_candidate_set(
                reasoning, candidate_set_id="m46:set", candidates=(candidate,)
            )

    def test_unknown_hypothesis_reference_is_rejected(self):
        reasoning = self._reasoning()
        candidate = InitiativeCandidate(
            "m46:candidate",
            reasoning.reasoning_id,
            "Investigate the observed condition.",
            supporting_hypothesis_ids=("unknown:hypothesis",),
        )
        with self.assertRaises(ValueError):
            build_initiative_candidate_set(
                reasoning, candidate_set_id="m46:set", candidates=(candidate,)
            )

    def test_uncertainty_is_carried_forward(self):
        reasoning = self._reasoning()
        candidate = InitiativeCandidate(
            "m46:candidate",
            reasoning.reasoning_id,
            "Investigate the observed condition.",
            supporting_hypothesis_ids=("m46:hypothesis",),
        )
        result = build_initiative_candidate_set(
            reasoning, candidate_set_id="m46:set", candidates=(candidate,)
        )
        self.assertEqual(result.unresolved_uncertainties, reasoning.unresolved_uncertainties)
        payload = result.to_context()
        self.assertFalse(payload["intent_established"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["execution_requested"])

    def test_candidate_output_is_not_authorization_or_execution(self):
        reasoning = self._reasoning()
        result = build_initiative_candidate_set(
            reasoning,
            candidate_set_id="m46:set",
            candidates=(
                InitiativeCandidate(
                    "m46:candidate",
                    reasoning.reasoning_id,
                    "Investigate the observed condition.",
                    supporting_hypothesis_ids=("m46:hypothesis",),
                ),
            ),
        )
        payload = result.candidates[0].to_context()
        self.assertFalse(payload["truth_established"])
        self.assertFalse(payload["intent_established"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["permissions_granted"])
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["execution_requested"])
