import unittest

from src.context.interpretation_semantics import (
    Interpretation,
    InterpretationConflict,
    MissingInformation,
    SupportReference,
)
from src.context.prioritization_semantics import (
    Prioritization,
    PriorityKind,
    PrioritySignal,
    PriorityTarget,
)
from src.context.proposed_consequence_semantics import (
    ConsequenceKind,
    ProposedConsequence,
    ProposedConsequenceProjector,
    ProposedConsequenceValidator,
    ProposedConsequences,
    ProposalSupport,
)
from src.context.reasoning_semantics import EpistemicRole, ReasoningContext, ReasoningInput


class ProposedConsequenceSemanticsTests(unittest.TestCase):
    def _reasoning_context(self):
        return ReasoningContext(
            request="inspect config",
            inputs=(
                ReasoningInput(
                    content="Config may be stale.",
                    source_type="MEMORY",
                    provenance={"source_id": "memory-store"},
                    epistemic_role=EpistemicRole.PERSISTED_CLAIM,
                ),
            ),
        )

    def _prioritization(self):
        return Prioritization(
            request="inspect config",
            targets=(
                PriorityTarget(
                    "missing:0",
                    PriorityKind.MISSING_INFORMATION,
                    "Need the current file path.",
                    PrioritySignal(importance=0.9, unresolved=1.0),
                    0,
                ),
            ),
        )

    def test_proposal_is_action_shaped_but_not_authorized(self):
        proposal = ProposedConsequence(
            "Obtain the current file path.",
            ConsequenceKind.ASK,
            (ProposalSupport("missing_information", "0"),),
        )
        context = proposal.to_context()
        self.assertEqual(context["epistemic_role"], "proposed")
        self.assertFalse(context["authorization"])

    def test_projector_uses_top_attention_target(self):
        result = ProposedConsequenceProjector().project(
            self._reasoning_context(), self._prioritization()
        )
        self.assertEqual(len(result.proposals), 1)
        self.assertEqual(result.proposals[0].priority_target_id, "missing:0")
        self.assertEqual(result.proposals[0].kind, ConsequenceKind.PLAN)

    def test_conflict_produces_investigation_proposal(self):
        interpretation = Interpretation(
            request="inspect config",
            conflicts=(
                InterpretationConflict(
                    "Memory conflicts with current evidence.",
                    (SupportReference(0),),
                ),
            ),
        )
        result = ProposedConsequenceProjector().project(
            self._reasoning_context(), self._prioritization(), interpretation
        )
        self.assertEqual(result.proposals[1].kind, ConsequenceKind.INVESTIGATE)

    def test_missing_information_produces_question_proposal(self):
        interpretation = Interpretation(
            request="inspect config",
            missing_information=(MissingInformation("Need the current path.", 0.8),),
        )
        result = ProposedConsequenceProjector().project(
            self._reasoning_context(), self._prioritization(), interpretation
        )
        self.assertEqual(result.proposals[1].kind, ConsequenceKind.ASK)

    def test_request_boundaries_are_preserved(self):
        prioritization = Prioritization(
            request="different request",
            targets=(),
        )
        with self.assertRaises(ValueError):
            ProposedConsequenceProjector().project(self._reasoning_context(), prioritization)

    def test_priority_support_must_reference_supplied_prioritization(self):
        proposal = ProposedConsequences(
            request="inspect config",
            proposals=(
                ProposedConsequence(
                    "Address target",
                    ConsequenceKind.PLAN,
                    (ProposalSupport("prioritization", "unknown"),),
                    priority_target_id="unknown",
                ),
            ),
        )
        with self.assertRaises(ValueError):
            ProposedConsequenceValidator().validate(
                self._reasoning_context(), self._prioritization(), proposal
            )

    def test_forbidden_execution_controls_are_rejected(self):
        with self.assertRaises(ValueError):
            ProposedConsequence(
                "Run the tool.",
                ConsequenceKind.PLAN,
                metadata={"execute": True},
            )

    def test_proposals_serialize_without_execution_payload(self):
        proposal = ProposedConsequences(
            request="inspect config",
            proposals=(
                ProposedConsequence("Prepare a plan.", ConsequenceKind.PLAN),
            ),
        )
        context = proposal.to_context()
        serialized = context["proposals"][0]
        self.assertIn("epistemic_role", serialized)
        self.assertFalse(serialized["authorization"])
        self.assertNotIn("tool_handle", serialized)
        self.assertNotIn("execute", serialized)


if __name__ == "__main__":
    unittest.main()
