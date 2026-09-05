import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
)
from src.core.environment_world_model_rollback_repair_retry_execution_attempt import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus,
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


class EnvironmentWorldModelRollbackRepairRetryExecutionAttemptTests(unittest.TestCase):
    def setUp(self):
        self.preparation = EnvironmentWorldModelRollbackRepairRetryExecutionPreparation(
            preparation_id="preparation1",
            environment_id="env1",
            authorization_decision_id="decision1",
            authorization_integrity_id="integrity1",
            proposal_id="proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            eligible=True,
            evaluated_at=__import__("datetime").datetime(2026, 9, 5, 20, 0, tzinfo=__import__("datetime").timezone.utc),
            next_eligible_at=None,
            reasons={"status": "ready"},
            lineage={"source": {"stage": "m23.42"}},
        )

    def test_successful_executor_produces_completed_attempt(self):
        executor = FakeExecutor(observed={"repaired": True})
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(executor).attempt(self.preparation)
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED)
        self.assertTrue(result.completed)
        self.assertTrue(result.execution_attempted)
        self.assertEqual(result.observed_result["repaired"], True)
        self.assertEqual(executor.calls, [self.preparation])

    def test_executor_exception_becomes_failed_attempt(self):
        executor = FakeExecutor(error=RuntimeError("repair failed"))
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(executor).attempt(
            self.preparation, worker_id="worker1"
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED)
        self.assertFalse(result.completed)
        self.assertEqual(result.reason, "repair failed")
        self.assertEqual(result.worker_id, "worker1")

    def test_execution_identity_is_deterministic_for_same_preparation(self):
        a = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(FakeExecutor(observed=True)).attempt(self.preparation)
        b = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(FakeExecutor(observed=False)).attempt(self.preparation)
        self.assertEqual(a.execution_id, b.execution_id)
        self.assertNotEqual(a.execution_id, self.preparation.preparation_id)

    def test_source_preparation_is_not_mutated(self):
        executor = FakeExecutor(observed={"ok": True})
        before = self.preparation
        EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(executor).attempt(self.preparation)
        self.assertEqual(before, self.preparation)
        self.assertEqual(self.preparation.preparation_id, "preparation1")

    def test_nested_result_and_lineage_are_frozen(self):
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(
            FakeExecutor(observed={"nested": {"value": [1, 2]}})
        ).attempt(self.preparation, lineage={"nested": {"source": "executor"}})
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"
        with self.assertRaises(TypeError):
            result.observed_result["nested"]["value"][0] = 9

    def test_worker_identity_is_optional_and_not_authority(self):
        result = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(
            FakeExecutor(observed="done")
        ).attempt(self.preparation)
        self.assertIsNone(result.worker_id)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.mutates_persistence)

    def test_wrong_upstream_type_fails_closed(self):
        service = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(FakeExecutor(observed=True))
        with self.assertRaises(TypeError):
            service.attempt(object())

    def test_executor_contract_is_required(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(object())

    def test_worker_id_must_be_non_empty_when_supplied(self):
        service = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService(FakeExecutor(observed=True))
        with self.assertRaises(ValueError):
            service.attempt(self.preparation, worker_id=" ")

    def test_failed_artifact_requires_reason(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
                execution_id="exec1",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
            )

    def test_completed_artifact_cannot_have_failure_reason(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
                execution_id="exec1",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
                observed_result=True,
                reason="bad",
            )


if __name__ == "__main__":
    unittest.main()
