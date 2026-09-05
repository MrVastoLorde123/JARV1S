from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission import (
    DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus,
)


class M22_48_Tests(unittest.TestCase):
    def setUp(self) -> None:
        from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation import (
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
        )

        evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-1", feedback_id="feedback-1", outcome_id="outcome-1", execution_id="execution-1",
            preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
            evaluation_id_from_feedback="evaluation-from-feedback-1", decision_source_evaluation_id="decision-source-1",
            source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1", source_execution_id="source-execution-1", source_admission_id="source-admission-1",
            proposal_source_id="proposal-source-1", domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
            confidence=0.8, evidence={"observed": True}, provenance={"source": "test"}, reason="success",
        )
        decision = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation=evaluation)
        )
        self.proposal = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService().propose(
            decision, {"change": "candidate"}, {"observed": True}, {"source": "test"}
        )
        assert self.proposal is not None
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService()

    def test_admitted_for_valid_proposal(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        self.assertEqual(admission.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED)

    def test_admission_id_is_deterministic(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal)
        self.assertEqual(self.service.admit(context).admission_id, self.service.admit(context).admission_id)

    def test_admission_id_is_distinct(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        self.assertNotEqual(admission.admission_id, admission.proposal_id)
        self.assertNotEqual(admission.admission_id, admission.decision_id)
        self.assertNotEqual(admission.admission_id, admission.evaluation_id)
        self.assertNotEqual(admission.admission_id, admission.feedback_id)
        self.assertNotEqual(admission.admission_id, admission.execution_id)

    def test_full_lineage_is_preserved(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        for name in (
            "proposal_id", "decision_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id", "preparation_id",
            "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id", "domain",
        ):
            self.assertEqual(getattr(admission, name), getattr(self.proposal, name))
        self.assertEqual(admission.source_policy_id, self.proposal.policy_id)
        self.assertEqual(admission.source_proposal_id, self.proposal.source_proposal_id)
        self.assertEqual(admission.source_admission_id, self.proposal.admission_id)

    def test_admission_is_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        with self.assertRaises(FrozenInstanceError):
            admission.reason = "changed"  # type: ignore[misc]

    def test_payload_is_recursively_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        with self.assertRaises(TypeError):
            admission.proposal["new"] = True  # type: ignore[index]

    def test_evidence_is_recursively_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        with self.assertRaises(TypeError):
            admission.evidence["new"] = True  # type: ignore[index]

    def test_provenance_is_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        with self.assertRaises(TypeError):
            admission.provenance["new"] = "blocked"  # type: ignore[index]

    def test_metadata_is_immutable(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        with self.assertRaises(TypeError):
            admission.metadata["new"] = True  # type: ignore[index]

    def test_context_freezes_related_context(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(
            proposal=self.proposal, related_context={"nested": {"value": True}}
        )
        with self.assertRaises(TypeError):
            context.related_context["new"] = True  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            context.proposal = self.proposal  # type: ignore[misc]

    def test_context_preserves_authority_wall(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        context = admission.to_context()
        for key in ("execution_authorized", "authorization_granted", "execution_requested", "retry_requested", "revocation_requested", "memory_mutation_allowed", "authority_granted"):
            self.assertFalse(context[key])

    def test_low_confidence_is_rejected(self) -> None:
        low = self.proposal.__class__(**{**self.proposal.__dict__, "confidence": 0.49, "proposal_id": "proposal-low"})
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=low))
        self.assertEqual(admission.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED)

    def test_empty_payload_is_rejected(self) -> None:
        bad = self.proposal.__class__(**{**self.proposal.__dict__, "payload": {}, "proposal_id": "proposal-empty"})
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=bad)
        admission = self.service.admit(context)
        self.assertEqual(admission.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED)

    def test_wrong_provider_identity_is_rejected(self) -> None:
        class _BadProvider(DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider):
            def admit(self, context):
                result = super().admit(context)
                object.__setattr__(result, "proposal_id", "wrong-proposal")
                return result

        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError):
            self.service.__class__(_BadProvider()).admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal={"bad": True})  # type: ignore[arg-type]

    def test_admission_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission(
                admission_id="admission-x", proposal_id="proposal-x", decision_id="decision-x", evaluation_id="evaluation-x",
                feedback_id="feedback-x", outcome_id="outcome-x", execution_id="execution-x", preparation_id="preparation-x",
                source_admission_id="admission-source-x", source_proposal_id="proposal-source-x", decision_source_evaluation_id="decision-source-x",
                evaluation_id_from_feedback="evaluation-from-feedback-x", source_feedback_id="source-feedback-x", candidate_id="candidate-x",
                source_candidate_id="source-candidate-x", execution_source_id="execution-source-x", source_execution_id="source-execution-x",
                domain="semantic", source_policy_id="source-policy-x", policy_id="policy-x",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED,
                reason="test", confidence=0.8, proposal={"x": 1}, evidence={"x": 1}, provenance={"source": "test"},
                execution_authorized=True,
            )

    def test_status_is_explicit(self) -> None:
        admission = self.service.admit(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext(proposal=self.proposal))
        self.assertEqual(admission.status.value, "admitted")


if __name__ == "__main__":
    unittest.main()
