from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_feedback import LearningWriteAdaptationFeedbackService
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationService,
)
from src.tools.learning_write_adaptation_evaluation_decision import (
    LearningWriteAdaptationEvaluationAction,
    LearningWriteAdaptationEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationDecisionService,
)
from src.tools.learning_write_adaptation_evaluation_proposal import (
    LearningWriteAdaptationEvaluationProposal,
    LearningWriteAdaptationEvaluationProposalContext,
    LearningWriteAdaptationEvaluationProposalError,
    LearningWriteAdaptationEvaluationProposalService,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)


class LearningWriteAdaptationEvaluationProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = LearningWriteAdaptationOutcome(
            execution_id="adapt-exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            source_candidate_id="source-candidate-1",
            domain="semantic",
            status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
            adaptation_result={"changed": True},
            result_fingerprint="fp-1",
        )
        feedback = LearningWriteAdaptationFeedbackService().from_outcome(outcome)
        evaluation = LearningWriteAdaptationFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationDecisionContext(evaluation=evaluation)
        )
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationAction.ACCEPT)
        self.decision = decision
        self.service = LearningWriteAdaptationEvaluationProposalService()
        self.payload = {"strategy": {"mode": "retain", "threshold": 0.5}}

    def test_accepted_decision_becomes_proposal(self) -> None:
        proposal = self.service.propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal=self.payload,
            )
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.proposal, self.payload)
        self.assertEqual(proposal.decision_id, self.decision.decision_id)

    def test_non_accepted_decision_is_not_proposed(self) -> None:
        deferred = self.decision.__class__(
            decision_id=self.decision.decision_id,
            evaluation_id=self.decision.evaluation_id,
            feedback_id=self.decision.feedback_id,
            source_feedback_id=self.decision.source_feedback_id,
            candidate_id=self.decision.candidate_id,
            execution_id=self.decision.execution_id,
            admission_id=self.decision.admission_id,
            proposal_id=self.decision.proposal_id,
            source_candidate_id=self.decision.source_candidate_id,
            domain=self.decision.domain,
            action=LearningWriteAdaptationEvaluationAction.DEFER,
            reason="await more evidence",
            confidence=self.decision.confidence,
            metadata=self.decision.metadata,
        )
        self.assertIsNone(
            self.service.propose(
                LearningWriteAdaptationEvaluationProposalContext(
                    decision=deferred,
                    proposal=self.payload,
                )
            )
        )

    def test_exact_lineage_is_preserved(self) -> None:
        proposal = self.service.propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal=self.payload,
            )
        )
        self.assertEqual(proposal.evaluation_id, self.decision.evaluation_id)
        self.assertEqual(proposal.feedback_id, self.decision.feedback_id)
        self.assertEqual(proposal.source_feedback_id, self.decision.source_feedback_id)
        self.assertEqual(proposal.candidate_id, self.decision.candidate_id)
        self.assertEqual(proposal.source_candidate_id, self.decision.source_candidate_id)
        self.assertEqual(proposal.execution_id, self.decision.execution_id)
        self.assertEqual(proposal.admission_id, self.decision.admission_id)
        self.assertEqual(proposal.proposal_id, self.decision.proposal_id)
        self.assertEqual(proposal.domain, self.decision.domain)

    def test_proposal_id_is_deterministic(self) -> None:
        context = LearningWriteAdaptationEvaluationProposalContext(
            decision=self.decision,
            proposal=self.payload,
        )
        first = self.service.propose(context)
        second = self.service.propose(context)
        self.assertEqual(first.proposal_id, second.proposal_id)

    def test_proposal_is_immutable(self) -> None:
        proposal = self.service.propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal=self.payload,
            )
        )
        with self.assertRaises(FrozenInstanceError):
            proposal.reason = "changed"  # type: ignore[misc]

    def test_nested_proposal_is_recursively_frozen(self) -> None:
        proposal = self.service.propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal={"nested": {"values": [1, 2, {"x": 3}]}},
            )
        )
        with self.assertRaises(TypeError):
            proposal.proposal["nested"]["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.proposal["nested"]["values"][2]["x"] = 4  # type: ignore[index]

    def test_evidence_and_provenance_are_recursively_frozen(self) -> None:
        proposal = self.service.propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal=self.payload,
            )
        )
        with self.assertRaises(TypeError):
            proposal.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.provenance["new"] = "x"  # type: ignore[index]

    def test_proposal_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalError):
            LearningWriteAdaptationEvaluationProposal(
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                execution_id="execution-x",
                admission_id="admission-x",
                source_candidate_id="source-candidate-x",
                domain="semantic",
                proposal={"x": 1},
                evidence={"x": 1},
                provenance={"source": "test"},
                confidence=0.5,
                reason="test",
                adaptation_authorized=True,
            )

    def test_context_is_immutable_and_payload_is_frozen(self) -> None:
        context = LearningWriteAdaptationEvaluationProposalContext(
            decision=self.decision,
            proposal={"a": {"b": 1}},
        )
        with self.assertRaises(FrozenInstanceError):
            context.proposal = {}  # type: ignore[misc]
        with self.assertRaises(TypeError):
            context.proposal["a"]["b"] = 2  # type: ignore[index]

    def test_empty_proposal_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalError):
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal={},
            )

    def test_invalid_decision_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalError):
            LearningWriteAdaptationEvaluationProposalContext(
                decision={"bad": True},  # type: ignore[arg-type]
                proposal=self.payload,
            )

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalError):
            LearningWriteAdaptationEvaluationProposalContext(
                decision=self.decision,
                proposal=["bad"],  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
