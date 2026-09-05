from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalError,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalService,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.decision = LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-source-1",
            decision_source_evaluation_id="historical-evaluation-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_id="execution-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-1",
            action=LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT,
            reason="sufficient observed evidence",
            confidence=0.8,
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackProposalService()

    def _context(self, proposal=None):
        return LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
            decision=self.decision,
            proposal=proposal or {"strategy": {"mode": "retain"}},
        )

    def _decision_with_action(self, action):
        return LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
            decision_id=self.decision.decision_id,
            evaluation_id=self.decision.evaluation_id,
            feedback_id=self.decision.feedback_id,
            preparation_id=self.decision.preparation_id,
            admission_id=self.decision.admission_id,
            proposal_id=self.decision.proposal_id,
            decision_source_evaluation_id=self.decision.decision_source_evaluation_id,
            source_feedback_id=self.decision.source_feedback_id,
            candidate_id=self.decision.candidate_id,
            source_candidate_id=self.decision.source_candidate_id,
            execution_id=self.decision.execution_id,
            source_execution_id=self.decision.source_execution_id,
            domain=self.decision.domain,
            policy_id=self.decision.policy_id,
            action=action,
            reason="need more evidence",
            confidence=self.decision.confidence,
        )

    def test_accepted_decision_creates_proposal(self) -> None:
        proposal = self.service.propose(self._context())
        self.assertIsInstance(proposal, LearningWriteAdaptationEvaluationExecutionFeedbackProposal)
        self.assertEqual(proposal.decision_id, self.decision.decision_id)

    def test_non_accept_decision_creates_no_proposal(self) -> None:
        for action in (
            LearningWriteAdaptationEvaluationExecutionFeedbackAction.DEFER,
            LearningWriteAdaptationEvaluationExecutionFeedbackAction.REJECT,
        ):
            decision = self._decision_with_action(action)
            self.assertIsNone(
                self.service.propose(
                    LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
                        decision=decision,
                        proposal={"strategy": "retain"},
                    )
                )
            )

    def test_full_lineage_is_preserved(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        for field in (
            "decision_id", "evaluation_id", "decision_source_evaluation_id", "feedback_id",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_id",
            "source_execution_id", "preparation_id", "admission_id", "domain", "policy_id",
        ):
            self.assertEqual(getattr(proposal, field), getattr(self.decision, field))
        self.assertEqual(proposal.proposal_source_id, self.decision.proposal_id)

    def test_proposal_id_is_deterministic(self) -> None:
        first = self.service.propose(self._context())
        second = self.service.propose(self._context())
        self.assertEqual(first.proposal_id, second.proposal_id)

    def test_proposal_id_changes_with_payload(self) -> None:
        first = self.service.propose(self._context({"strategy": "retain"}))
        second = self.service.propose(self._context({"strategy": "revise"}))
        self.assertNotEqual(first.proposal_id, second.proposal_id)

    def test_proposal_id_is_distinct_from_decision_id(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        self.assertNotEqual(proposal.proposal_id, self.decision.decision_id)

    def test_proposal_is_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        with self.assertRaises(FrozenInstanceError):
            proposal.domain = "other"  # type: ignore[misc]

    def test_proposal_payload_is_recursively_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        with self.assertRaises(TypeError):
            proposal.proposal["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.proposal["strategy"]["mode"] = "change"  # type: ignore[index]

    def test_evidence_and_provenance_are_recursively_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        with self.assertRaises(TypeError):
            proposal.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            proposal.provenance["new"] = "blocked"  # type: ignore[index]

    def test_proposal_requires_non_empty_payload(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackProposalError):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
                decision=self.decision,
                proposal={},
            )

    def test_proposal_context_is_immutable(self) -> None:
        context = self._context()
        with self.assertRaises(FrozenInstanceError):
            context.decision = self.decision  # type: ignore[misc]

    def test_authority_wall_is_preserved(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        context = proposal.to_context()
        self.assertFalse(context["adaptation_authorized"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])

    def test_proposal_preserves_policy_identity(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        self.assertEqual(proposal.policy_id, "policy-1")

    def test_invalid_decision_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackProposalError):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
                decision={"bad": True},  # type: ignore[arg-type]
                proposal={"x": 1},
            )

    def test_invalid_proposal_payload_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackProposalError):
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext(
                decision=self.decision,
                proposal=["bad"],  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
