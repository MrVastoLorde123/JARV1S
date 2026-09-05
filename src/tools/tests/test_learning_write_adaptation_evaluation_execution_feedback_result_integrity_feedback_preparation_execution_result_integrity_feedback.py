import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution_result_integrity import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus,
)


def integrity(**overrides):
    values = dict(
        integrity_id="integrity-1", execution_id="execution-1", preparation_id="preparation-1",
        admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
        evaluation_id="evaluation-1", feedback_id="feedback-1", outcome_id="outcome-1",
        source_admission_id="source-admission-1", source_proposal_id="source-proposal-1",
        decision_source_evaluation_id="decision-source-evaluation-1",
        evaluation_id_from_feedback="feedback-evaluation-1", source_feedback_id="source-feedback-1",
        candidate_id="candidate-1", source_candidate_id="source-candidate-1",
        execution_source_id="execution-source-1", source_execution_id="historical-execution-1",
        domain="learning", source_policy_id="source-policy-1", policy_id="policy-1",
        status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED,
        execution_result={"ok": True, "nested": {"value": 7}}, result_fingerprint="a" * 64,
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(**values)


class M22_52_Tests(unittest.TestCase):
    def test_success_creates_feedback(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        self.assertEqual(feedback.kind, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS)
        self.assertEqual(feedback.integrity_id, "integrity-1")

    def test_failure_creates_failure_feedback(self):
        source = integrity(status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED, execution_result=None, result_fingerprint=None, reason="boom")
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(source)
        self.assertEqual(feedback.kind, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE)
        self.assertEqual(feedback.payload["reason"], "boom")

    def test_wrong_integrity_type_is_rejected(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(object())

    def test_feedback_id_is_deterministic(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService()
        source = integrity()
        self.assertEqual(service.from_integrity(source).feedback_id, service.from_integrity(source).feedback_id)

    def test_feedback_id_is_distinct_from_integrity_id(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        self.assertNotEqual(feedback.feedback_id, feedback.integrity_id)

    def test_full_lineage_is_preserved(self):
        source = integrity()
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(source)
        fields = (
            "integrity_id", "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "source_admission_id", "source_proposal_id", "domain", "source_policy_id", "policy_id",
        )
        for field in fields:
            self.assertEqual(getattr(feedback, field), getattr(source, field))
        self.assertEqual(feedback.source_feedback_id, source.source_feedback_id)

    def test_payload_contains_observed_integrity_evidence(self):
        source = integrity()
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(source)
        self.assertEqual(feedback.payload["integrity_status"], source.status.value)
        self.assertEqual(feedback.payload["result_fingerprint"], source.result_fingerprint)
        self.assertEqual(feedback.payload["execution_result"], source.execution_result)

    def test_payload_is_recursively_immutable(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        with self.assertRaises((TypeError, AttributeError)):
            feedback.payload["execution_result"]["nested"]["value"] = 8

    def test_provenance_is_immutable(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        with self.assertRaises((TypeError, AttributeError)):
            feedback.provenance["extra"] = "bad"

    def test_feedback_is_frozen(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        with self.assertRaises(AttributeError):
            feedback.reason = "changed"

    def test_authority_wall(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        context = feedback.to_context()
        for key in ("authority_granted", "authorization_granted", "execution_requested", "retry_requested", "revocation_requested", "memory_mutation_allowed", "adaptation_truth_proven"):
            self.assertFalse(context[key])

    def test_feedback_does_not_authorize(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        self.assertFalse(hasattr(feedback, "authorization_granted"))

    def test_kind_is_explicit(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        self.assertIsInstance(feedback.kind, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind)

    def test_empty_payload_is_rejected(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(
                feedback_id="feedback-1", integrity_id="integrity-1", execution_id="execution-1", preparation_id="preparation-1",
                admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
                decision_source_evaluation_id="decision-source-evaluation-1", evaluation_id_from_feedback="feedback-evaluation-1",
                source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="execution-source-1", source_execution_id="historical-execution-1",
                source_admission_id="source-admission-1", source_proposal_id="source-proposal-1",
                domain="learning", source_policy_id="source-policy-1", policy_id="policy-1",
                kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS,
                payload={}, provenance={"source": "m22.52"}, reason="reason",
            )

    def test_metadata_context_preserves_feedback_identity(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService().from_integrity(integrity())
        context = feedback.to_context()
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id"], feedback.feedback_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_result_integrity_id"], feedback.integrity_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_feedback_decision_source_evaluation_id"], feedback.decision_source_evaluation_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_feedback_evaluation_id_from_feedback"], feedback.evaluation_id_from_feedback)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id"], feedback.feedback_id)


if __name__ == "__main__":
    unittest.main()
