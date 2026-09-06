import unittest
from datetime import datetime, timedelta, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_feedback import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackStatus,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationService,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment,
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentService,
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
    EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy,
    EnvironmentWorldModelRollbackRepairRetryState,
)


class EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 21, 0, tzinfo=timezone.utc)
        self.success = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation(
            evaluation_id="evaluation-success",
            feedback_id="feedback-success",
            outcome_id="outcome-success",
            execution_id="execution-success",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL,
            evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION,
            confidence=1.0,
            result_fingerprint="fp-success",
            failure_reason=None,
            reasons={"status": "success"},
            lineage={"nested": {"source": "feedback-success"}},
        )
        self.failure = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation(
            evaluation_id="evaluation-failure",
            feedback_id="feedback-failure",
            outcome_id="outcome-failure",
            execution_id="execution-failure",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL,
            evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION,
            confidence=1.0,
            result_fingerprint=None,
            failure_reason="provider unavailable",
            reasons={"status": "failure"},
            lineage={"nested": {"source": "feedback-failure"}},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentService()
        self.policy = EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy(
            max_retries=3,
            backoff_seconds=30.0,
        )

    def test_failure_evaluation_is_eligible_within_bounds(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1, last_attempt_at=self.now - timedelta(minutes=2)),
            assessment_id="assessment1",
            evaluated_at=self.now,
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE)
        self.assertEqual(result.next_eligible_at, self.now - timedelta(minutes=2) + timedelta(seconds=30))

    def test_failure_evaluation_waits_for_backoff(self) -> None:
        last_attempt = self.now - timedelta(seconds=10)
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1, last_attempt_at=last_attempt),
            assessment_id="assessment2",
            evaluated_at=self.now,
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING)
        self.assertEqual(result.next_eligible_at, last_attempt + timedelta(seconds=30))

    def test_failure_evaluation_is_not_eligible_after_limit(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=3, last_attempt_at=self.now),
            assessment_id="assessment3",
            evaluated_at=self.now,
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE)
        self.assertIsNone(result.next_eligible_at)

    def test_success_evaluation_does_not_reopen_retry(self) -> None:
        result = self.service.assess(
            self.success,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=0),
            assessment_id="assessment4",
            evaluated_at=self.now,
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE)
        self.assertIsNone(result.next_eligible_at)

    def test_no_previous_attempt_uses_current_time_as_baseline(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=0),
            assessment_id="assessment5",
            evaluated_at=self.now,
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE)
        self.assertEqual(result.next_eligible_at, self.now + timedelta(seconds=30))

    def test_custom_reasons_and_lineage_are_frozen(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
            assessment_id="assessment6",
            evaluated_at=self.now,
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "evaluation"}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertEqual(result.reasons["cause"], "validated")
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_assessment_is_immutable(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
            assessment_id="assessment7",
            evaluated_at=self.now,
        )
        with self.assertRaises(AttributeError):
            result.status = EnvironmentWorldModelRollbackRepairReeligibilityAssessmentStatus.NOT_ELIGIBLE

    def test_assessment_cannot_authorize_or_schedule(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
            assessment_id="assessment8",
            evaluated_at=self.now,
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)

    def test_lineage_from_evaluation_is_preserved(self) -> None:
        result = self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
            assessment_id="assessment9",
            evaluated_at=self.now,
        )
        self.assertEqual(result.evaluation_id, "evaluation-failure")
        self.assertEqual(result.feedback_id, "feedback-failure")
        self.assertEqual(result.outcome_id, "outcome-failure")
        self.assertEqual(result.environment_id, "env1")

    def test_source_evaluation_is_not_mutated(self) -> None:
        before = self.failure.lineage
        self.service.assess(
            self.failure,
            self.policy,
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
            assessment_id="assessment10",
            evaluated_at=self.now,
        )
        self.assertEqual(self.failure.lineage, before)

    def test_wrong_evaluation_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                object(),
                self.policy,
                EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
                assessment_id="assessment11",
                evaluated_at=self.now,
            )

    def test_wrong_policy_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                self.failure,
                object(),
                EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
                assessment_id="assessment12",
                evaluated_at=self.now,
            )

    def test_wrong_state_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                self.failure,
                self.policy,
                object(),
                assessment_id="assessment13",
                evaluated_at=self.now,
            )

    def test_aware_timestamp_is_required(self) -> None:
        with self.assertRaises(ValueError):
            self.service.assess(
                self.failure,
                self.policy,
                EnvironmentWorldModelRollbackRepairRetryState(retry_count=1),
                assessment_id="assessment14",
                evaluated_at=datetime(2026, 9, 5, 21, 0),
            )

    def test_policy_and_state_bounds_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy(max_retries=-1)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryState(retry_count=-1)

    def test_constructor_rejects_invalid_status_type(self) -> None:
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment(
                assessment_id="assessment15",
                evaluation_id="evaluation-failure",
                feedback_id="feedback-failure",
                outcome_id="outcome-failure",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION,
                retry_count=1,
                max_retries=3,
                evaluated_at=self.now,
                next_eligible_at=None,
                status="ELIGIBLE",
            )


if __name__ == "__main__":
    unittest.main()
