import unittest

from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2,
)
from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status,
)


class M23_56FeedbackV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.success_integrity = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id="integrity1",
            execution_id="execution1",
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_decision_id="decision-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id=None,
            outcome_id="outcome1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED,
            integrity_status="VALID",
            result_fingerprint="abc123",
            worker_id="worker1",
        )
        self.failure_integrity = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id="integrity2",
            execution_id="execution2",
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_decision_id="decision-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id=None,
            outcome_id="outcome2",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED,
            integrity_status="VALID",
            failure_reason="provider unavailable",
            worker_id="worker1",
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status

    def _outcome(self, integrity, outcome_id):
        from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
            EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service,
        )
        return EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service().classify(
            integrity, outcome_id=outcome_id
        )

    def test_success_outcome_records_success_signal_and_preserves_v2_chain(self) -> None:
        outcome = self._outcome(self.success_integrity, "outcome-success")
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(
            outcome, feedback_id="feedback1"
        )
        self.assertEqual(feedback.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL)
        self.assertEqual(feedback.outcome_status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS)
        self.assertEqual(feedback.integrity_id, "integrity1")
        self.assertEqual(feedback.decision_id, "decision1")
        self.assertEqual(feedback.proposal_id, "proposal1")
        self.assertEqual(feedback.result_fingerprint, "abc123")

    def test_failure_outcome_records_failure_signal_and_preserves_reason(self) -> None:
        outcome = self._outcome(self.failure_integrity, "outcome-failure")
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(
            outcome, feedback_id="feedback2"
        )
        self.assertEqual(feedback.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL)
        self.assertEqual(feedback.outcome_status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE)
        self.assertEqual(feedback.failure_reason, "provider unavailable")
        self.assertIsNone(feedback.result_fingerprint)

    def test_feedback_is_immutable_and_advisory(self) -> None:
        outcome = self._outcome(self.success_integrity, "outcome-immutable")
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(
            outcome, feedback_id="feedback3"
        )
        with self.assertRaises(AttributeError):
            feedback.feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL
        self.assertTrue(feedback.is_advisory_only)
        self.assertFalse(feedback.recommends_retry)
        self.assertFalse(feedback.requests_retry)
        self.assertFalse(feedback.grants_authority)
        self.assertFalse(feedback.mutates_policy)
        self.assertFalse(feedback.mutates_persistence)

    def test_source_outcome_is_not_mutated_and_feedback_id_is_required(self) -> None:
        outcome = self._outcome(self.success_integrity, "outcome-source")
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(outcome, feedback_id="")
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(
            outcome, feedback_id="feedback4"
        )
        self.assertEqual(outcome.outcome_id, "outcome-source")
        self.assertEqual(outcome.status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS)
        self.assertEqual(feedback.outcome_id, "outcome-source")

    def test_nested_lineage_is_frozen_and_signal_cannot_mismatch_outcome(self) -> None:
        outcome = self._outcome(self.success_integrity, "outcome-lineage")
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service().record(
            outcome,
            feedback_id="feedback5",
            lineage={"nested": {"execution": "execution1"}},
        )
        self.assertEqual(feedback.lineage["nested"]["execution"], "execution1")
        with self.assertRaises(TypeError):
            feedback.lineage["nested"]["execution"] = "changed"
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
                feedback_id="bad",
                outcome_id="outcome-lineage",
                integrity_id="integrity1",
                execution_id="execution1",
                preparation_id="preparation1",
                decision_id="decision1",
                integrity_decision_id="decision-integrity1",
                proposal_id="proposal1",
                assessment_id="assessment1",
                evaluation_id="evaluation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                outcome_status=EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS,
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL,
                failure_reason="bad mismatch",
            )


if __name__ == "__main__":
    unittest.main()
