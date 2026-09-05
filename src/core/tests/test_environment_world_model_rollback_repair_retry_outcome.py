import unittest
from datetime import datetime, timezone

from src.core.environment_world_model_rollback_repair_retry_execution_attempt import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus,
)
from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity,
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService,
)
from src.core.environment_world_model_rollback_repair_retry_outcome import (
    EnvironmentWorldModelRollbackRepairRetryOutcome,
    EnvironmentWorldModelRollbackRepairRetryOutcomeError,
    EnvironmentWorldModelRollbackRepairRetryOutcomeService,
    EnvironmentWorldModelRollbackRepairRetryOutcomeStatus,
)


class EnvironmentWorldModelRollbackRepairRetryOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        preparation = EnvironmentWorldModelRollbackRepairRetryExecutionPreparation(
            preparation_id="preparation1",
            environment_id="env1",
            authorization_decision_id="decision1",
            authorization_integrity_id="integrity-auth1",
            proposal_id="proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            eligible=True,
            evaluated_at=datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc),
            next_eligible_at=datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc),
        )
        attempt = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="execution1",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"repaired": True},
            worker_id="worker1",
        )
        self.preparation = preparation
        self.integrity_service = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService()
        self.integrity = self.integrity_service.verify(preparation, attempt, integrity_id="integrity1")
        self.service = EnvironmentWorldModelRollbackRepairRetryOutcomeService()

    def test_completed_integrity_classifies_as_success(self) -> None:
        result = self.service.classify(self.integrity, outcome_id="outcome1")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.SUCCESS)
        self.assertTrue(result.is_observational)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.mutates_persistence)

    def test_failed_integrity_classifies_as_failure(self) -> None:
        attempt = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="execution2",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
            reason="provider unavailable",
            worker_id="worker1",
        )
        integrity = self.integrity_service.verify(self.preparation, attempt, integrity_id="integrity2")
        result = self.service.classify(integrity, outcome_id="outcome2")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE)
        self.assertEqual(result.failure_reason, "provider unavailable")
        self.assertIsNone(result.result_fingerprint)

    def test_invalid_integrity_cannot_be_classified(self) -> None:
        invalid = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity(
            integrity_id="bad-integrity",
            execution_id="execution1",
            preparation_id="wrong",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            integrity_status="INVALID",
            result_fingerprint=None,
            failure_reason=None,
            worker_id=None,
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryOutcomeError):
            self.service.classify(invalid, outcome_id="outcome3")

    def test_outcome_id_must_be_non_empty(self) -> None:
        with self.assertRaises(ValueError):
            self.service.classify(self.integrity, outcome_id="")

    def test_result_fingerprint_is_preserved(self) -> None:
        result = self.service.classify(self.integrity, outcome_id="outcome4")
        self.assertEqual(result.result_fingerprint, self.integrity.result_fingerprint)

    def test_integrity_lineage_is_preserved(self) -> None:
        result = self.service.classify(
            self.integrity,
            outcome_id="outcome5",
            lineage={"nested": {"source": "integrity"}},
        )
        self.assertEqual(result.lineage["nested"]["source"], "integrity")
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_result_is_immutable(self) -> None:
        result = self.service.classify(self.integrity, outcome_id="outcome6")
        with self.assertRaises(AttributeError):
            result.status = EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE

    def test_constructor_rejects_success_without_fingerprint(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryOutcome(
                outcome_id="outcome7",
                integrity_id="integrity1",
                execution_id="execution1",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
                status=EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.SUCCESS,
                result_fingerprint=None,
            )

    def test_constructor_rejects_failure_with_fingerprint(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryOutcome(
                outcome_id="outcome8",
                integrity_id="integrity2",
                execution_id="execution2",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
                status=EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE,
                result_fingerprint="abc",
                failure_reason="failed",
            )

    def test_source_integrity_is_not_mutated(self) -> None:
        self.service.classify(self.integrity, outcome_id="outcome9")
        self.assertEqual(self.integrity.integrity_id, "integrity1")
        self.assertEqual(self.integrity.integrity_status, "VALID")


if __name__ == "__main__":
    unittest.main()
