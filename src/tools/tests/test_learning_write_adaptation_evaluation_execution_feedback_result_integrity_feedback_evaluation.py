from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)


class M22_45_Tests(unittest.TestCase):
    def setUp(self) -> None:
        common = dict(
            outcome_id="outcome-1", execution_id="execution-1", preparation_id="preparation-1",
            admission_id="admission-1", proposal_id="proposal-1", decision_id="decision-1",
            evaluation_id="evaluation-1", decision_source_evaluation_id="historical-evaluation-1",
            source_feedback_id="source-feedback-1", candidate_id="candidate-1",
            source_candidate_id="source-candidate-1", execution_source_id="execution-source-1",
            source_execution_id="source-execution-1", source_admission_id="source-admission-1",
            proposal_source_id="source-proposal-1", domain="semantic", source_policy_id="source-policy-1",
            policy_id="policy-1",
        )
        self.success = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(
            feedback_id="feedback-1",
            kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS,
            payload={"outcome_status": "succeeded", "execution_result": {"changed": True}, "result_fingerprint": "fp"},
            provenance={"source": "test"}, reason="successful result-integrity evidence", **common,
        )
        failure_data = {**common, "outcome_id": "outcome-2", "execution_id": "execution-2", "feedback_id": "feedback-2"}
        self.failure = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(
            kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE,
            payload={"outcome_status": "failed", "reason": "bad execution"},
            provenance={"source": "test"},
            reason="failed result-integrity evidence",
            **failure_data,
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService()

    def test_success_feedback_becomes_integrity_success_signal(self) -> None:
        result = self.service.evaluate(self.success)
        self.assertEqual(
            result.signal,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
        )
        self.assertEqual(result.confidence, 0.5)
        self.assertEqual(result.evidence["payload"]["execution_result"]["changed"], True)

    def test_failure_feedback_becomes_integrity_failure_signal(self) -> None:
        result = self.service.evaluate(self.failure)
        self.assertEqual(
            result.signal,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL,
        )
        self.assertEqual(result.evidence["payload"]["reason"], "bad execution")

    def test_full_lineage_is_preserved(self) -> None:
        result = self.service.evaluate(self.success)
        for field in (
            "feedback_id", "outcome_id", "execution_id", "preparation_id", "admission_id",
            "proposal_id", "decision_id", "evaluation_id_from_feedback", "decision_source_evaluation_id",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id",
            "source_execution_id", "source_admission_id", "proposal_source_id", "domain",
            "source_policy_id", "policy_id",
        ):
            source_field = "evaluation_id" if field == "evaluation_id_from_feedback" else field
            self.assertEqual(getattr(result, field), getattr(self.success, source_field))

    def test_evaluation_id_is_deterministic(self) -> None:
        self.assertEqual(self.service.evaluate(self.success).evaluation_id, self.service.evaluate(self.success).evaluation_id)

    def test_evaluation_id_is_distinct_from_feedback_and_execution(self) -> None:
        result = self.service.evaluate(self.success)
        self.assertNotEqual(result.evaluation_id, self.success.feedback_id)
        self.assertNotEqual(result.evaluation_id, self.success.execution_id)

    def test_observed_payload_is_preserved(self) -> None:
        result = self.service.evaluate(self.success)
        self.assertEqual(result.evidence["payload"]["result_fingerprint"], "fp")

    def test_evaluation_is_immutable(self) -> None:
        result = self.service.evaluate(self.success)
        with self.assertRaises(FrozenInstanceError):
            result.confidence = 0.9  # type: ignore[misc]

    def test_evidence_is_recursively_immutable(self) -> None:
        result = self.service.evaluate(self.success)
        with self.assertRaises(TypeError):
            result.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            result.evidence["payload"]["new"] = True  # type: ignore[index]

    def test_provenance_is_immutable(self) -> None:
        result = self.service.evaluate(self.success)
        with self.assertRaises(TypeError):
            result.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_preserves_authority_wall(self) -> None:
        context = self.service.evaluate(self.success).to_context()
        for key in (
            "feedback_evaluation_observed", "adaptation_truth_proven", "authority_granted",
            "authorization_granted", "execution_requested", "retry_requested",
            "revocation_requested", "memory_mutation_allowed",
        ):
            self.assertEqual(context[key], key == "feedback_evaluation_observed")

    def test_invalid_feedback_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate({"bad": True})  # type: ignore[arg-type]

    def test_invalid_signal_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
                evaluation_id="eval", feedback_id="feedback", outcome_id="outcome", execution_id="execution",
                preparation_id="prep", admission_id="admission", proposal_id="proposal", decision_id="decision",
                evaluation_id_from_feedback="evaluation-source", decision_source_evaluation_id="historical-evaluation",
                source_feedback_id="source-feedback", candidate_id="candidate", source_candidate_id="source-candidate",
                execution_source_id="execution-source", source_execution_id="source-execution",
                source_admission_id="source-admission", proposal_source_id="source-proposal", domain="semantic",
                source_policy_id="source-policy", policy_id="policy", signal="bad", confidence=0.5,
                evidence={}, provenance={"source": "test"}, reason="test",
            )  # type: ignore[arg-type]

    def test_confidence_must_be_bounded(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
                evaluation_id="eval", feedback_id="feedback", outcome_id="outcome", execution_id="execution",
                preparation_id="prep", admission_id="admission", proposal_id="proposal", decision_id="decision",
                evaluation_id_from_feedback="evaluation-source", decision_source_evaluation_id="historical-evaluation",
                source_feedback_id="source-feedback", candidate_id="candidate", source_candidate_id="source-candidate",
                execution_source_id="execution-source", source_execution_id="source-execution",
                source_admission_id="source-admission", proposal_source_id="source-proposal", domain="semantic",
                source_policy_id="source-policy", policy_id="policy",
                signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
                confidence=1.1, evidence={}, provenance={"source": "test"}, reason="test",
            )


if __name__ == "__main__":
    unittest.main()
