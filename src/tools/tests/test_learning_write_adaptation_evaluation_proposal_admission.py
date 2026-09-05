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
from src.tools.learning_write_adaptation_feedback import LearningWriteAdaptationFeedbackService
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationService,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)
from src.tools.learning_write_adaptation_evaluation_proposal_admission import (
    LearningWriteAdaptationEvaluationProposalAdmission,
    LearningWriteAdaptationEvaluationProposalAdmissionContext,
    LearningWriteAdaptationEvaluationProposalAdmissionError,
    LearningWriteAdaptationEvaluationProposalAdmissionService,
    LearningWriteAdaptationEvaluationProposalAdmissionStatus,
)


class LearningWriteAdaptationEvaluationProposalAdmissionTests(unittest.TestCase):
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
        self.service = LearningWriteAdaptationEvaluationProposalAdmissionService()

    def test_admitted_proposal_returns_admitted_result(self) -> None:
        admission = self.service.admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(
                proposal=self.proposal
            )
        )
        self.assertEqual(
            admission.status,
            LearningWriteAdaptationEvaluationProposalAdmissionStatus.ADMITTED,
        )
        self.assertTrue(admission.reason)

    def test_exact_lineage_is_preserved(self) -> None:
        admission = self.service.admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(
                proposal=self.proposal
            )
        )
        self.assertEqual(admission.proposal_id, self.proposal.proposal_id)
        self.assertEqual(admission.decision_id, self.proposal.decision_id)
        self.assertEqual(admission.evaluation_id, self.proposal.evaluation_id)
        self.assertEqual(admission.feedback_id, self.proposal.feedback_id)
        self.assertEqual(admission.source_feedback_id, self.proposal.source_feedback_id)
        self.assertEqual(admission.candidate_id, self.proposal.candidate_id)
        self.assertEqual(admission.source_candidate_id, self.proposal.source_candidate_id)
        self.assertEqual(admission.execution_id, self.proposal.execution_id)
        self.assertEqual(admission.domain, self.proposal.domain)

    def test_admission_id_is_deterministic(self) -> None:
        context = LearningWriteAdaptationEvaluationProposalAdmissionContext(
            proposal=self.proposal
        )
        first = self.service.admit(context)
        second = self.service.admit(context)
        self.assertEqual(first.admission_id, second.admission_id)

    def test_admission_is_immutable(self) -> None:
        admission = self.service.admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(
                proposal=self.proposal
            )
        )
        with self.assertRaises(FrozenInstanceError):
            admission.reason = "changed"  # type: ignore[misc]

    def test_admission_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalAdmissionError):
            LearningWriteAdaptationEvaluationProposalAdmission(
                admission_id="admission-x",
                proposal_id="proposal-x",
                decision_id="decision-x",
                evaluation_id="evaluation-x",
                feedback_id="feedback-x",
                source_feedback_id="source-feedback-x",
                candidate_id="candidate-x",
                execution_id="execution-x",
                source_candidate_id="source-candidate-x",
                domain="semantic",
                status=LearningWriteAdaptationEvaluationProposalAdmissionStatus.ADMITTED,
                reason="test",
                confidence=0.5,
                policy_id="policy-x",
                authorization_granted=True,
            )

    def test_low_confidence_proposal_is_rejected(self) -> None:
        low = self.proposal.__class__(
            proposal_id=self.proposal.proposal_id,
            decision_id=self.proposal.decision_id,
            evaluation_id=self.proposal.evaluation_id,
            feedback_id=self.proposal.feedback_id,
            source_feedback_id=self.proposal.source_feedback_id,
            candidate_id=self.proposal.candidate_id,
            execution_id=self.proposal.execution_id,
            admission_id=self.proposal.admission_id,
            source_candidate_id=self.proposal.source_candidate_id,
            domain=self.proposal.domain,
            proposal=self.proposal.proposal,
            evidence=self.proposal.evidence,
            provenance=self.proposal.provenance,
            confidence=0.49,
            reason=self.proposal.reason,
        )
        admission = self.service.admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(proposal=low)
        )
        self.assertEqual(
            admission.status,
            LearningWriteAdaptationEvaluationProposalAdmissionStatus.REJECTED,
        )

    def test_related_context_is_frozen(self) -> None:
        context = LearningWriteAdaptationEvaluationProposalAdmissionContext(
            proposal=self.proposal,
            related_context={"nested": {"value": 1}},
        )
        with self.assertRaises(FrozenInstanceError):
            context.proposal = None  # type: ignore[assignment]
        with self.assertRaises(TypeError):
            context.related_context["nested"]["value"] = 2  # type: ignore[index]

    def test_provider_output_identity_is_validated(self) -> None:
        class BadProvider:
            def admit(self, context):
                result = self.service_result(context)
                return result.__class__(
                    admission_id=result.admission_id,
                    proposal_id="wrong",
                    decision_id=result.decision_id,
                    evaluation_id=result.evaluation_id,
                    feedback_id=result.feedback_id,
                    source_feedback_id=result.source_feedback_id,
                    candidate_id=result.candidate_id,
                    execution_id=result.execution_id,
                    source_candidate_id=result.source_candidate_id,
                    domain=result.domain,
                    status=result.status,
                    reason=result.reason,
                    confidence=result.confidence,
                    policy_id=result.policy_id,
                    metadata=result.metadata,
                )

            @staticmethod
            def service_result(context):
                from src.tools.learning_write_adaptation_evaluation_proposal_admission import (
                    DeterministicLearningWriteAdaptationEvaluationProposalAdmissionProvider,
                )
                return DeterministicLearningWriteAdaptationEvaluationProposalAdmissionProvider().admit(context)

        bad_service = LearningWriteAdaptationEvaluationProposalAdmissionService(BadProvider())
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalAdmissionError):
            bad_service.admit(
                LearningWriteAdaptationEvaluationProposalAdmissionContext(
                    proposal=self.proposal
                )
            )

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.admit({"bad": True})  # type: ignore[arg-type]

    def test_context_requires_proposal_type(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationProposalAdmissionError):
            LearningWriteAdaptationEvaluationProposalAdmissionContext(
                proposal={"bad": True},  # type: ignore[arg-type]
            )

    def test_context_related_data_accepts_empty_default(self) -> None:
        context = LearningWriteAdaptationEvaluationProposalAdmissionContext(
            proposal=self.proposal
        )
        self.assertEqual(dict(context.related_context), {})


if __name__ == "__main__":
    unittest.main()
