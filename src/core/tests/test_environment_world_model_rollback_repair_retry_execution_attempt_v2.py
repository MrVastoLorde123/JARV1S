import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_execution_preparation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2,
)
from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)


class FakeExecutor:
    def __init__(self, observed=None, error=None):
        self.observed = observed
        self.error = error
        self.calls = []

    def execute(self, preparation):
        self.calls.append(preparation)
        if self.error is not None:
            raise self.error
        return self.observed


class M23_53ExecutionAttemptV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.preparation = EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2(
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_id="integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id="feedback1",
            outcome_id="outcome1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            assessment_status="ELIGIBLE",
            eligible=True,
            retry_count=1,
            max_retries=3,
            evaluated_at=datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc),
            next_eligible_at=None,
            reasons={"status": "ready"},
            lineage={"source": {"stage": "m23.52"}},
        )

    def test_successful_executor_produces_completed_attempt_and_receives_exact_preparation(self) -> None:
        executor = FakeExecutor(observed={"repaired": True})
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(executor).attempt(self.preparation)
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED)
        self.assertTrue(result.completed)
        self.assertTrue(result.execution_attempted)
        self.assertEqual(result.observed_result["repaired"], True)
        self.assertEqual(executor.calls, [self.preparation])
        self.assertEqual(result.decision_id, "decision1")
        self.assertEqual(result.integrity_id, "integrity1")
        self.assertEqual(result.assessment_id, "assessment1")
        self.assertEqual(result.evaluation_id, "evaluation1")
        self.assertEqual(result.feedback_id, "feedback1")
        self.assertEqual(result.outcome_id, "outcome1")

    def test_executor_exception_becomes_failed_attempt(self) -> None:
        executor = FakeExecutor(error=RuntimeError("repair failed"))
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(executor).attempt(
            self.preparation, worker_id="worker1"
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED)
        self.assertFalse(result.completed)
        self.assertEqual(result.failure_reason, "repair failed")
        self.assertEqual(result.worker_id, "worker1")
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_execution_authority)

    def test_execution_identity_is_deterministic_and_distinct_from_preparation(self) -> None:
        a = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(FakeExecutor(observed=True)).attempt(self.preparation)
        b = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(FakeExecutor(observed=False)).attempt(self.preparation)
        self.assertEqual(a.execution_id, b.execution_id)
        self.assertNotEqual(a.execution_id, self.preparation.preparation_id)
        self.assertTrue(a.execution_id.startswith("retry-exec-v2-"))

    def test_invalid_preparation_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(FakeExecutor()).attempt(object())

    def test_result_and_observed_data_are_immutable(self) -> None:
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Service(
            FakeExecutor(observed={"nested": [1, {"value": 2}]})
        ).attempt(self.preparation)
        self.assertTrue(isinstance(result.lineage, MappingProxyType))
        self.assertTrue(isinstance(result.observed_result["nested"], tuple))
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.mutates_persistence)


if __name__ == "__main__":
    unittest.main()
