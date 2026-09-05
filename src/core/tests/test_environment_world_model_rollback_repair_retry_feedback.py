import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_outcome import (
    EnvironmentWorldModelRollbackRepairRetryOutcome,
)
from src.core.environment_world_model_rollback_repair_retry_feedback import (
    EnvironmentWorldModelRollbackRepairRetryFeedback,
    EnvironmentWorldModelRollbackRepairRetryFeedbackService,
    EnvironmentWorldModelRollbackRepairRetryFeedbackStatus,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.success = EnvironmentWorldModelRollbackRepairRetryOutcome(
            outcome_id="outcome1",
            execution_id="retry-exec1",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status="SUCCESS",
            result_fingerprint="fp123",
            failure_reason=None,
            worker_id="worker1",
            reasons={"status": "success"},
            lineage={"integrity": "ri1"},
        )
        self.failure = EnvironmentWorldModelRollbackRepairRetryOutcome(
            outcome_id="outcome2",
            execution_id="retry-exec2",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status="FAILURE",
            result_fingerprint=None,
            failure_reason="repair provider unavailable",
            worker_id="worker1",
            reasons={"status": "failure"},
            lineage={"integrity": "ri2"},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryFeedbackService()

    def test_success_outcome_becomes_success_signal(self) -> None:
        result = self.service.record(self.success, feedback_id="feedback1")
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL)
        self.assertEqual(result.result_fingerprint, "fp123")
        self.assertIsNone(result.failure_reason)

    def test_failure_outcome_becomes_failure_signal(self) -> None:
        result = self.service.record(self.failure, feedback_id="feedback2")
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL)
        self.assertIsNone(result.result_fingerprint)
        self.assertEqual(result.failure_reason, "repair provider unavailable")

    def test_result_and_execution_lineage_are_preserved(self) -> None:
        result = self.service.record(self.success, feedback_id="feedback3")
        self.assertEqual(result.outcome_id, "outcome1")
        self.assertEqual(result.execution_id, "retry-exec1")
        self.assertEqual(result.preparation_id, "preparation1")
        self.assertEqual(result.environment_id, "env1")

    def test_custom_reasons_and_lineage_are_frozen(self) -> None:
        result = self.service.record(
            self.success,
            feedback_id="feedback4",
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "outcome"}},
        )
        self.assertEqual(result.reasons["cause"], "validated")
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_result_is_immutable(self) -> None:
        result = self.service.record(self.success, feedback_id="feedback5")
        with self.assertRaises(AttributeError):
            result.feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL

    def test_feedback_id_must_be_non_empty(self) -> None:
        with self.assertRaises(ValueError):
            self.service.record(self.success, feedback_id=" ")

    def test_wrong_outcome_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.record(object(), feedback_id="feedback7")

    def test_feedback_cannot_recommend_or_request_retry(self) -> None:
        result = self.service.record(self.failure, feedback_id="feedback8")
        self.assertFalse(result.recommends_retry)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.mutates_persistence)

    def test_constructor_rejects_success_without_fingerprint(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedback(
                feedback_id="bad1",
                outcome_id="outcome1",
                execution_id="exec1",
                preparation_id="prep1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                outcome_status="SUCCESS",
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL,
                result_fingerprint=None,
            )

    def test_constructor_rejects_failure_with_fingerprint(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedback(
                feedback_id="bad2",
                outcome_id="outcome2",
                execution_id="exec2",
                preparation_id="prep1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                outcome_status="FAILURE",
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL,
                result_fingerprint="fp",
                failure_reason="failed",
            )

    def test_source_outcome_is_not_mutated(self) -> None:
        before = self.success.lineage
        self.service.record(self.success, feedback_id="feedback10")
        self.assertEqual(self.success.lineage, before)


if __name__ == "__main__":
    unittest.main()
