from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_decision import (
    LearningWriteAdaptationEvaluationAction,
    LearningWriteAdaptationEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationDecisionService,
)
from src.tools.learning_write_adaptation_evaluation_proposal import (
    LearningWriteAdaptationEvaluationProposalContext,
    LearningWriteAdaptationEvaluationProposalService,
)
from src.tools.learning_write_adaptation_evaluation_proposal_admission import (
    LearningWriteAdaptationEvaluationProposalAdmissionContext,
    LearningWriteAdaptationEvaluationProposalAdmissionService,
)
from src.tools.learning_write_adaptation_evaluation_execution_preparation import (
    LearningWriteAdaptationEvaluationExecutionPreparation,
    LearningWriteAdaptationEvaluationExecutionPreparationError,
    LearningWriteAdaptationEvaluationExecutionPreparationService,
)
from src.tools.learning_write_adaptation_feedback import LearningWriteAdaptationFeedbackService
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationService,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionPreparationTests(unittest.TestCase):
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
        proposal = LearningWriteAdaptationEvaluationProposalService().propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=decision,
                proposal={"strategy": {"mode": "retain"}},
            )
        )
        self.assertIsNotNone(proposal)
        self.proposal = proposal
        self.admission = LearningWriteAdaptationEvaluationProposalAdmissionService().admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(
                proposal=self.proposal
            )
        )
        self.service = LearningWriteAdaptationEvaluationExecutionPreparationService()

    def test_admitted_proposal_prepares_handoff(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        self.assertIsInstance(prepared, LearningWriteAdaptationEvaluationExecutionPreparation)
        self.assertTrue(prepared.preparation_id)
        self.assertEqual(dict(prepared.payload), {"strategy": {"mode": "retain"}})

    def test_rejected_admission_cannot_prepare(self) -> None:
        rejected = self.admission.__class__(
            admission_id=self.admission.admission_id,
            proposal_id=self.admission.proposal_id,
            decision_id=self.admission.decision_id,
            evaluation_id=self.admission.evaluation_id,
            feedback_id=self.admission.feedback_id,
            source_feedback_id=self.admission.source_feedback_id,
            candidate_id=self.admission.candidate_id,
            execution_id=self.admission.execution_id,
            source_candidate_id=self.admission.source_candidate_id,
            domain=self.admission.domain,
            status=self.admission.status.REJECTED,
            reason="rejected for test",
            confidence=self.admission.confidence,
            policy_id=self.admission.policy_id,
            metadata=self.admission.metadata,
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionPreparationError):
            self.service.prepare(self.proposal, rejected)

    def test_exact_lineage_is_preserved(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        self.assertEqual(prepared.admission_id, self.admission.admission_id)
        self.assertEqual(prepared.proposal_id, self.proposal.proposal_id)
        self.assertEqual(prepared.decision_id, self.proposal.decision_id)
        self.assertEqual(prepared.evaluation_id, self.proposal.evaluation_id)
        self.assertEqual(prepared.feedback_id, self.proposal.feedback_id)
        self.assertEqual(prepared.source_feedback_id, self.proposal.source_feedback_id)
        self.assertEqual(prepared.candidate_id, self.proposal.candidate_id)
        self.assertEqual(prepared.source_candidate_id, self.proposal.source_candidate_id)
        self.assertEqual(prepared.source_execution_id, self.proposal.execution_id)
        self.assertEqual(prepared.domain, self.proposal.domain)
        self.assertEqual(prepared.policy_id, self.admission.policy_id)

    def test_preparation_id_is_deterministic(self) -> None:
        first = self.service.prepare(self.proposal, self.admission)
        second = self.service.prepare(self.proposal, self.admission)
        self.assertEqual(first.preparation_id, second.preparation_id)

    def test_preparation_id_is_distinct_from_source_execution_id(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        self.assertNotEqual(prepared.preparation_id, prepared.source_execution_id)

    def test_preparation_is_immutable(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        with self.assertRaises(FrozenInstanceError):
            prepared.domain = "other"  # type: ignore[misc]

    def test_payload_is_recursively_frozen(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        with self.assertRaises(TypeError):
            prepared.payload["strategy"]["mode"] = "changed"  # type: ignore[index]

    def test_identity_mismatch_is_rejected(self) -> None:
        mismatched = self.admission.__class__(
            admission_id=self.admission.admission_id,
            proposal_id="wrong-proposal",
            decision_id=self.admission.decision_id,
            evaluation_id=self.admission.evaluation_id,
            feedback_id=self.admission.feedback_id,
            source_feedback_id=self.admission.source_feedback_id,
            candidate_id=self.admission.candidate_id,
            execution_id=self.admission.execution_id,
            source_candidate_id=self.admission.source_candidate_id,
            domain=self.admission.domain,
            status=self.admission.status,
            reason=self.admission.reason,
            confidence=self.admission.confidence,
            policy_id=self.admission.policy_id,
            metadata=self.admission.metadata,
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionPreparationError):
            self.service.prepare(self.proposal, mismatched)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.prepare(self.proposal, object())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.service.prepare(object(), self.admission)  # type: ignore[arg-type]

    def test_preparation_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionPreparationError):
            LearningWriteAdaptationEvaluationExecutionPreparation(
                preparation_id="prep-x",
                admission_id="admission-x",
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                source_candidate_id="source-candidate-x",
                source_execution_id="execution-x",
                domain="semantic",
                policy_id="policy-x",
                payload={"strategy": "retain"},
                execution_authorized=True,
            )

    def test_to_context_marks_execution_unstarted(self) -> None:
        prepared = self.service.prepare(self.proposal, self.admission)
        context = prepared.to_context()
        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["execution_authorized"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])


if __name__ == "__main__":
    unittest.main()
