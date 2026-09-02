import unittest

from src.context.interpretation_semantics import (
    DerivedClaim,
    Interpretation,
    InterpretationConflict,
    InterpretationStatus,
    MissingInformation,
    SupportReference,
    Uncertainty,
)
from src.context.prioritization_semantics import (
    Prioritization,
    PrioritizationProjector,
    PrioritizationValidator,
    PriorityKind,
    PrioritySignal,
    PriorityTarget,
)
from src.context.reasoning_semantics import EpistemicRole, ReasoningContext, ReasoningInput


class PrioritizationSemanticsTests(unittest.TestCase):
    def _context(self):
        return ReasoningContext(
            request="resolve config issue",
            inputs=(
                ReasoningInput(
                    content="A stale memory says config is under src/old.",
                    source_type="MEMORY",
                    relevance_score=0.9,
                    importance=0.4,
                    epistemic_role=EpistemicRole.PERSISTED_CLAIM,
                ),
                ReasoningInput(
                    content="Current observation says config.py is under src/core.",
                    source_type="OBSERVATION",
                    relevance_score=1.0,
                    importance=0.9,
                    epistemic_role=EpistemicRole.OBSERVED,
                ),
            ),
            observations=(
                ReasoningInput(
                    content="The last inspection failed to find the old path.",
                    source_type="OBSERVATION",
                    relevance_score=1.0,
                    importance=0.8,
                    epistemic_role=EpistemicRole.OBSERVED,
                ),
            ),
            current_state={
                "execution_state": {"status": "FAILED"},
            },
        )

    def test_attention_is_ordered_without_authorization(self):
        prioritization = PrioritizationProjector().project(self._context())
        PrioritizationValidator().validate(self._context(), prioritization)

        self.assertEqual(tuple(t.rank for t in prioritization.targets), tuple(range(len(prioritization.targets))))
        self.assertEqual(prioritization.targets[0].kind, PriorityKind.OBSERVATION)
        self.assertEqual(prioritization.metadata["prioritization_semantics"], "m7.3")
        for target in prioritization.targets:
            self.assertNotIn("authorize", target.metadata)
            self.assertNotIn("execute", target.metadata)

    def test_conflict_uncertainty_missing_information_receive_attention(self):
        interpretation = Interpretation(
            request="resolve config issue",
            claims=(DerivedClaim(
                "The old memory is probably outdated.",
                (SupportReference(0),),
                confidence=0.8,
                status=InterpretationStatus.UNCERTAIN,
            ),),
            uncertainties=(Uncertainty("The current file path still needs confirmation.", severity=0.9),),
            conflicts=(InterpretationConflict(
                "Memory conflicts with current observation.",
                (SupportReference(0), SupportReference(1)),
            ),),
            missing_information=(MissingInformation("Need filesystem search result.", importance=0.95),),
        )
        prioritization = PrioritizationProjector().project(self._context(), interpretation)
        kinds = {target.kind for target in prioritization.targets}

        self.assertIn(PriorityKind.UNCERTAINTY, kinds)
        self.assertIn(PriorityKind.CONFLICT, kinds)
        self.assertIn(PriorityKind.MISSING_INFORMATION, kinds)

    def test_interpretation_request_must_match(self):
        interpretation = Interpretation("different request")
        with self.assertRaises(ValueError):
            PrioritizationProjector().project(self._context(), interpretation)

    def test_signal_components_are_bounded(self):
        with self.assertRaises(ValueError):
            PrioritySignal(urgency=1.1)
        self.assertEqual(PrioritySignal().score, 0.0)

    def test_prioritization_rejects_bad_ranking(self):
        first = PriorityTarget("a", PriorityKind.INPUT, "a", PrioritySignal(relevance=0.2), 0)
        second = PriorityTarget("b", PriorityKind.INPUT, "b", PrioritySignal(relevance=0.9), 1)
        prioritization = Prioritization("resolve config issue", (first, second))
        with self.assertRaises(ValueError):
            PrioritizationValidator().validate(self._context(), prioritization)

    def test_serialization_is_provider_neutral(self):
        prioritization = PrioritizationProjector().project(self._context())
        serialized = prioritization.to_context()

        self.assertEqual(serialized["request"], "resolve config issue")
        self.assertIn("score", serialized["targets"][0]["signal"])
        self.assertEqual(serialized["targets"][0]["rank"], 0)


if __name__ == "__main__":
    unittest.main()
