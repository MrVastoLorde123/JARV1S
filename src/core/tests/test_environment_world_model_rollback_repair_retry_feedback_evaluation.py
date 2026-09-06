import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_feedback import (
    EnvironmentWorldModelRollbackRepairRetryFeedback,
    EnvironmentWorldModelRollbackRepairRetryFeedbackStatus,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationService,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.success = EnvironmentWorldModelRollbackRepairRetryFeedback(
            feedback_id="feedback1",
            outcome_id="outcome1",
            execution_id="execution1",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status="SUCCESS",
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL,
            result_fingerprint="fp123",
            failure_reason=None,
            reasons={"status": "success"},
            lineage={"nested": {"source": "outcome1"}},
        )
        self.failure = EnvironmentWorldModelRollbackRepairRetryFeedback(
            feedback_id="feedback2",
            outcome_id="outcome2",
            execution_id="execution2",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status="FAILURE",
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL,
            result_fingerprint=None,
            failure_reason="repair provider unavailable",
            reasons={"status": "failure"},
            lineage={"nested": {"source": "outcome2"}},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationService()

    def test_success_feedback_becomes_success_evaluation(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation1")
        self.assertEqual(
            result.evaluation_status,
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION,
        )
        self.assertEqual(result.result_fingerprint, "fp123")
        self.assertEqual(result.confidence, 1.0)

    def test_failure_feedback_becomes_failure_evaluation(self) -> None:
        result = self.service.evaluate(self.failure, evaluation_id="evaluation2")
        self.assertEqual(
            result.evaluation_status,
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION,
        )
        self.assertEqual(result.failure_reason, "repair provider unavailable")
        self.assertIsNone(result.result_fingerprint)

    def test_lineage_is_preserved(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation3")
        self.assertEqual(result.feedback_id, "feedback1")
        self.assertEqual(result.outcome_id, "outcome1")
        self.assertEqual(result.execution_id, "execution1")
        self.assertEqual(result.preparation_id, "preparation1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")

    def test_custom_reasons_and_lineage_are_frozen(self) -> None:
        result = self.service.evaluate(
            self.success,
            evaluation_id="evaluation4",
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "feedback"}},
        )
        self.assertEqual(result.reasons["cause"], "validated")
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_evaluation_is_immutable(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation5")
        with self.assertRaises(AttributeError):
            result.evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION

    def test_evaluation_id_must_be_non_empty(self) -> None:
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id=" ")

    def test_wrong_feedback_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate(object(), evaluation_id="evaluation7")

    def test_confidence_is_bounded(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation8", confidence=0.75)
        self.assertEqual(result.confidence, 0.75)
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id="evaluation9", confidence=1.1)
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id="evaluation10", confidence=-0.1)

    def test_evaluation_cannot_authorize_or_request_retry(self) -> None:
        result = self.service.evaluate(self.failure, evaluation_id="evaluation11")
        self.assertTrue(result.is_observational)
        self.assertFalse(result.recommends_retry)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.mutates_persistence)

    def test_source_feedback_is_not_mutated(self) -> None:
        before = self.success.lineage
        self.service.evaluate(self.success, evaluation_id="evaluation12")
        self.assertEqual(self.success.lineage, before)

    def test_constructor_rejects_mismatched_status(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation(
                evaluation_id="bad1",
                feedback_id="feedback1",
                outcome_id="outcome1",
                execution_id="execution1",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION,
                confidence=1.0,
                result_fingerprint="fp123",
            )

    def test_constructor_rejects_non_numeric_confidence(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation(
                evaluation_id="bad2",
                feedback_id="feedback1",
                outcome_id="outcome1",
                execution_id="execution1",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION,
                confidence=True,
                result_fingerprint="fp123",
            )


if __name__ == "__main__":
    unittest.main()
