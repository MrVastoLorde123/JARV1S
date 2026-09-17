"""M45 reasoning and uncertainty contract tests."""

import unittest

from src.agency.current_context import CurrentContext, CurrentContextFact
from src.agency.reasoning import ReasoningHypothesis, build_reasoning_result
from src.agency.world_model import WorldModelFact
from src.agency.world_model_qualification import WorldFactQualification


class M45ReasoningTests(unittest.TestCase):
    def _context(self) -> CurrentContext:
        fact = WorldModelFact(
            "device:status",
            "device",
            "status",
            "online",
            ("observation:1",),
        )
        return CurrentContext(
            context_id="context:1",
            model_id="model:1",
            assessed_at="2026-09-16T21:00:00+00:00",
            facts=(CurrentContextFact(fact, WorldFactQualification.USABLE),),
        )

    def test_reasoning_requires_current_context_fact_lineage(self) -> None:
        context = self._context()
        hypothesis = ReasoningHypothesis(
            "hypothesis:1",
            "The device is available.",
            0.8,
            supporting_fact_ids=("device:status",),
        )
        result = build_reasoning_result(
            context,
            reasoning_id="reasoning:1",
            hypotheses=(hypothesis,),
        )
        self.assertEqual(result.context_id, context.context_id)
        self.assertEqual(result.hypothesis_count, 1)

    def test_unknown_fact_reference_is_rejected(self) -> None:
        context = self._context()
        hypothesis = ReasoningHypothesis(
            "hypothesis:1",
            "The unknown device is available.",
            0.5,
            supporting_fact_ids=("unknown:fact",),
        )
        with self.assertRaises(ValueError):
            build_reasoning_result(
                context,
                reasoning_id="reasoning:1",
                hypotheses=(hypothesis,),
            )

    def test_confidence_is_bounded_and_is_not_truth(self) -> None:
        with self.assertRaises(ValueError):
            ReasoningHypothesis("hypothesis:1", "x", 1.1)
        context = self._context()
        result = build_reasoning_result(
            context,
            reasoning_id="reasoning:1",
            hypotheses=(ReasoningHypothesis("hypothesis:1", "x", 0.2),),
        )
        payload = result.to_context()
        self.assertFalse(payload["truth_established"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["intent_established"])
        self.assertFalse(payload["execution_requested"])

    def test_uncertainty_is_preserved_not_resolved(self) -> None:
        context = self._context()
        result = build_reasoning_result(
            context,
            reasoning_id="reasoning:1",
            unresolved_uncertainties=("availability requires independent verification",),
        )
        self.assertEqual(
            result.unresolved_uncertainties,
            ("availability requires independent verification",),
        )

    def test_hypothesis_cannot_reference_same_fact_as_support_and_contradiction(self) -> None:
        with self.assertRaises(ValueError):
            ReasoningHypothesis(
                "hypothesis:1",
                "conflicted",
                0.4,
                supporting_fact_ids=("fact:1",),
                contradicting_fact_ids=("fact:1",),
            )


if __name__ == "__main__":
    unittest.main()
