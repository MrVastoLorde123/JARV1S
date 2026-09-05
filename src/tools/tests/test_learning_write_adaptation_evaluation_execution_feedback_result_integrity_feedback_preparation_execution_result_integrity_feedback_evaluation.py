import unittest

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)


def feedback(**overrides):
    values = dict(
        feedback_id="feedback-1", integrity_id="integrity-1", execution_id="execution-1", preparation_id="preparation-1",
        admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
        evaluation_id="upstream-evaluation-1", decision_source_evaluation_id="decision-source-evaluation-1",
        evaluation_id_from_feedback="feedback-evaluation-1", source_feedback_id="source-feedback-1",
        candidate_id="candidate-1", source_candidate_id="source-candidate-1", execution_source_id="execution-source-1",
        source_execution_id="historical-execution-1", source_admission_id="source-admission-1", proposal_source_id="source-proposal-1",
        domain="learning", source_policy_id="source-policy-1", policy_id="policy-1",
        kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS,
        payload={"integrity_status": "succeeded", "execution_result": {"ok": True}, "result_fingerprint": "a" * 64},
        provenance={"source": "m22.52", "integrity_id": "integrity-1"},
        reason="observed result-integrity feedback",
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(**values)


class M22_53_Tests(unittest.TestCase):
    def test_success_evaluates_to_success_signal(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        self.assertEqual(out.signal, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL)
        self.assertEqual(out.confidence, 0.5)

    def test_failure_evaluates_to_failure_signal(self):
        source = feedback(
            kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE,
            payload={"integrity_status": "failed", "reason": "boom"},
            reason="observed failed result-integrity feedback",
        )
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(source)
        self.assertEqual(out.signal, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL)

    def test_wrong_feedback_type_is_rejected(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(object())

    def test_full_lineage_is_preserved(self):
        source = feedback()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(source)
        for field in (
            "feedback_id", "integrity_id", "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id_from_feedback", "decision_source_evaluation_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id", "source_admission_id", "proposal_source_id",
            "domain", "source_policy_id", "policy_id",
        ):
            self.assertEqual(getattr(out, field), getattr(source, field))

    def test_evaluation_id_is_deterministic_and_distinct(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService()
        source = feedback()
        first = service.evaluate(source)
        second = service.evaluate(source)
        self.assertEqual(first.evaluation_id, second.evaluation_id)
        self.assertNotEqual(first.evaluation_id, source.evaluation_id)

    def test_evidence_contains_feedback_observation(self):
        source = feedback()
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(source)
        self.assertEqual(out.evidence["feedback_kind"], source.kind.value)
        self.assertEqual(out.evidence["payload"], source.payload)
        self.assertEqual(out.evidence["feedback_reason"], source.reason)

    def test_evidence_is_recursively_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        with self.assertRaises((TypeError, AttributeError)):
            out.evidence["payload"]["execution_result"]["ok"] = False

    def test_provenance_is_immutable(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        with self.assertRaises((TypeError, AttributeError)):
            out.provenance["extra"] = "bad"

    def test_confidence_is_bounded(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
                evaluation_id="eval", feedback_id="feedback", integrity_id="integrity", execution_id="exec", preparation_id="prep",
                admission_id="admission", proposal_id="proposal", decision_id="decision", evaluation_id_from_feedback="eval-fb",
                decision_source_evaluation_id="decision-eval", source_feedback_id="source-fb", candidate_id="candidate",
                source_candidate_id="source-candidate", execution_source_id="source-exec", source_execution_id="historical",
                source_admission_id="source-admission", proposal_source_id="source-proposal", domain="learning",
                source_policy_id="source-policy", policy_id="policy",
                signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
                confidence=1.1, evidence={"x": 1}, provenance={"source": "test"}, reason="reason",
            )

    def test_evaluation_is_frozen(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        with self.assertRaises(AttributeError):
            out.reason = "changed"

    def test_authority_wall(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback()).to_context()
        for key in ("authority_granted", "authorization_granted", "execution_requested", "retry_requested", "revocation_requested", "memory_mutation_allowed", "adaptation_truth_proven"):
            self.assertFalse(context[key])

    def test_evaluation_does_not_establish_truth(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        self.assertFalse(out.to_context()["adaptation_truth_proven"])

    def test_context_preserves_evaluation_identity(self):
        out = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService().evaluate(feedback())
        context = out.to_context()
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id"], out.evaluation_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_result_integrity_id"], out.integrity_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id"], out.feedback_id)


if __name__ == "__main__":
    unittest.main()
