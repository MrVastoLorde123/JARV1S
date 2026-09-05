from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_admission import (
    LearningWriteAdaptationAdmission,
    LearningWriteAdaptationAdmissionContext,
    LearningWriteAdaptationAdmissionError,
    LearningWriteAdaptationAdmissionService,
    LearningWriteAdaptationAdmissionStatus,
)
from src.tools.learning_write_adaptation_decision import LearningWriteAdaptationAction
from src.tools.learning_write_adaptation_proposal import (
    LearningWriteAdaptationProposalContext,
    LearningWriteAdaptationProposalService,
)


class LearningWriteAdaptationAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = self._proposal()
        self.service = LearningWriteAdaptationAdmissionService()

    def _proposal(self):
        from src.tools.learning_write_adaptation_decision import (
            LearningWriteAdaptationDecisionContext,
            LearningWriteAdaptationDecisionService,
        )
        from src.tools.learning_write_feedback import LearningWriteFeedbackService
        from src.tools.learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus
        from src.tools.learning_write_feedback_evaluation import LearningWriteFeedbackEvaluationService

        outcome = LearningWriteOutcome(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            status=LearningWriteOutcomeStatus.SUCCEEDED,
            write_result={"memory_id": 42},
            result_fingerprint="fp-1",
        )
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
        candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationDecisionService().decide(
            LearningWriteAdaptationDecisionContext(candidate=candidate)
        )
        return LearningWriteAdaptationProposalService().propose(
            LearningWriteAdaptationProposalContext(
                decision=decision,
                candidate=candidate,
                adaptation={"confidence_delta": 0.1, "strategy": "prefer_cached_result"},
            )
        )

    def test_admitted_proposal(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(self.proposal))
        self.assertEqual(admission.status, LearningWriteAdaptationAdmissionStatus.ADMITTED)

    def test_empty_adaptation_is_rejected(self) -> None:
        proposal = self.proposal.__class__(
            **{**self.proposal.__dict__, "adaptation": {}}
        )
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(proposal))
        self.assertEqual(admission.status, LearningWriteAdaptationAdmissionStatus.REJECTED)

    def test_low_confidence_is_rejected(self) -> None:
        proposal = self.proposal.__class__(
            **{**self.proposal.__dict__, "confidence": 0.4}
        )
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(proposal))
        self.assertEqual(admission.status, LearningWriteAdaptationAdmissionStatus.REJECTED)

    def test_exact_lineage_is_preserved(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(self.proposal))
        self.assertEqual(admission.proposal_id, self.proposal.proposal_id)
        self.assertEqual(admission.decision_id, self.proposal.decision_id)
        self.assertEqual(admission.candidate_id, self.proposal.candidate_id)
        self.assertEqual(admission.feedback_id, self.proposal.feedback_id)
        self.assertEqual(admission.execution_id, self.proposal.execution_id)
        self.assertEqual(admission.domain, self.proposal.domain)

    def test_admission_id_is_deterministic(self) -> None:
        context = LearningWriteAdaptationAdmissionContext(self.proposal)
        first = self.service.admit(context)
        second = self.service.admit(context)
        self.assertEqual(first.admission_id, second.admission_id)

    def test_admission_is_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(self.proposal))
        with self.assertRaises(FrozenInstanceError):
            admission.status = LearningWriteAdaptationAdmissionStatus.REJECTED  # type: ignore[misc]

    def test_admission_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationAdmissionError):
            LearningWriteAdaptationAdmission(
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                execution_id="exec-1",
                domain="semantic",
                status=LearningWriteAdaptationAdmissionStatus.ADMITTED,
                reason="bad",
                confidence=0.5,
                policy_id="policy",
                adaptation_write_allowed=True,
            )

    def test_admission_is_non_writing_and_non_authorizing(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(self.proposal))
        context = admission.to_context()
        self.assertFalse(context["adaptation_write_allowed"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_provider_identity_mismatch_is_rejected(self) -> None:
        class BadProvider:
            def admit(self, context):
                admission = LearningWriteAdaptationAdmissionService().admit(context)
                return LearningWriteAdaptationAdmission(
                    **{**admission.__dict__, "proposal_id": "wrong"}
                )

        with self.assertRaises(LearningWriteAdaptationAdmissionError):
            LearningWriteAdaptationAdmissionService(BadProvider()).admit(
                LearningWriteAdaptationAdmissionContext(self.proposal)
            )

    def test_invalid_context_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.admit(self.proposal)  # type: ignore[arg-type]

    def test_failure_explains_rejection(self) -> None:
        proposal = self.proposal.__class__(
            **{**self.proposal.__dict__, "evidence": {}}
        )
        admission = self.service.admit(LearningWriteAdaptationAdmissionContext(proposal))
        self.assertEqual(admission.status, LearningWriteAdaptationAdmissionStatus.REJECTED)
        self.assertIn("evidence", admission.reason)


if __name__ == "__main__":
    unittest.main()
