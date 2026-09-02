import unittest

from src.context.interpretation_semantics import (
    DerivedClaim,
    Interpretation,
    InterpretationConflict,
    InterpretationStatus,
    InterpretationValidator,
    MissingInformation,
    SupportReference,
    Uncertainty,
)
from src.context.reasoning_semantics import ReasoningContext, ReasoningInput, EpistemicRole, Freshness


class InterpretationSemanticsTests(unittest.TestCase):
    def _reasoning_context(self):
        return ReasoningContext(
            request="inspect config",
            inputs=(
                ReasoningInput(
                    content="Config is under src/core.",
                    source_type="MEMORY",
                    provenance={"source_id": "memory-store"},
                    epistemic_role=EpistemicRole.PERSISTED_CLAIM,
                    freshness=Freshness.UNKNOWN,
                ),
                ReasoningInput(
                    content="config.py was found.",
                    source_type="OBSERVATION",
                    provenance={"event_id": "obs-1"},
                    epistemic_role=EpistemicRole.OBSERVED,
                    freshness=Freshness.FRESH,
                    authority_allowed=True,
                ),
            ),
        )

    def test_supported_claim_requires_explicit_support(self):
        context = self._reasoning_context()
        interpretation = Interpretation(
            request="inspect config",
            claims=(DerivedClaim("The config likely exists in src/core.", (SupportReference(0),)),),
        )
        InterpretationValidator().validate(context, interpretation)

    def test_support_reference_must_point_inside_reasoning_context(self):
        context = self._reasoning_context()
        interpretation = Interpretation(
            request="inspect config",
            claims=(DerivedClaim("unsupported", (SupportReference(2),)),),
        )
        with self.assertRaises(ValueError):
            InterpretationValidator().validate(context, interpretation)

    def test_conflict_and_uncertainty_are_first_class_outputs(self):
        interpretation = Interpretation(
            request="inspect config",
            uncertainties=(Uncertainty("The memory may be stale.", (SupportReference(0),), 0.8),),
            conflicts=(InterpretationConflict(
                "Persistent memory and observed state disagree.",
                (SupportReference(0), SupportReference(1)),
            ),),
            missing_information=(MissingInformation("Need the current file path.", 0.9),),
        )
        context = self._reasoning_context()
        InterpretationValidator().validate(context, interpretation)
        self.assertEqual(len(interpretation.uncertainties), 1)
        self.assertEqual(len(interpretation.conflicts), 1)
        self.assertEqual(len(interpretation.missing_information), 1)

    def test_interpretation_is_not_authoritative_fact(self):
        interpretation = Interpretation(
            request="inspect config",
            claims=(DerivedClaim(
                "The config is probably under src/core.",
                (SupportReference(0),),
                confidence=0.99,
                status=InterpretationStatus.SUPPORTED,
            ),),
        )
        context = interpretation.to_context()
        self.assertEqual(context["claims"][0]["epistemic_role"], "derived")
        self.assertNotIn("authority_allowed", context["claims"][0])

    def test_request_must_match_reasoning_context(self):
        context = self._reasoning_context()
        interpretation = Interpretation("different request")
        with self.assertRaises(ValueError):
            InterpretationValidator().validate(context, interpretation)

    def test_provider_neutral_serialization_preserves_support_and_status(self):
        interpretation = Interpretation(
            request="inspect config",
            claims=(DerivedClaim(
                "The observed file supports the requested inspection.",
                (SupportReference(1, "supports"),),
                confidence=0.9,
            ),),
        )
        serialized = interpretation.to_context()
        self.assertEqual(serialized["claims"][0]["support"][0]["input_index"], 1)
        self.assertEqual(serialized["claims"][0]["status"], "supported")


if __name__ == "__main__":
    unittest.main()
