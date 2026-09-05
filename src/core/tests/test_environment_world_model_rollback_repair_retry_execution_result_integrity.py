import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_execution_attempt import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptService,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus,
)
from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity,
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityError,
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService,
)


class StubExecutor:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self.calls = 0

    def execute(self, preparation):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.value


class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preparation = EnvironmentWorldModelRollbackRepairRetryExecutionPreparation(
            preparation_id="preparation1",
            environment_id="env1",
            authorization_decision_id="decision1",
            authorization_integrity_id="integrity-auth1",
            proposal_id="proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            eligible=True,
            evaluated_at=__import__("datetime").datetime(2026, 9, 5, 20, 0, tzinfo=__import__("datetime").timezone.utc),
            next_eligible_at=__import__("datetime").datetime(2026, 9, 5, 20, 0, 20, tzinfo=__import__("datetime").timezone.utc),
            reasons={"status": "prepared"},
            lineage={"source": "execution-preparation"},
        )
        self.attempt = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec1",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"changed": True, "nested": {"value": 42}},
            worker_id="worker1",
            lineage={"source": "attempt"},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService()

    def test_completed_attempt_produces_valid_fingerprint(self) -> None:
        result = self.service.verify(self.preparation, self.attempt, integrity_id="result-integrity1")
        self.assertEqual(result.integrity_status, "VALID")
        self.assertTrue(result.observed_result_integrity)
        self.assertTrue(result.result_fingerprint)
        self.assertIsNone(result.failure_reason)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)

    def test_failed_attempt_requires_reason_and_produces_valid_integrity(self) -> None:
        failed = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec2",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
            reason="repair provider unavailable",
            worker_id="worker1",
        )
        result = self.service.verify(self.preparation, failed, integrity_id="result-integrity2")
        self.assertEqual(result.integrity_status, "VALID")
        self.assertIsNone(result.result_fingerprint)
        self.assertEqual(result.failure_reason, "repair provider unavailable")

    def test_identity_mismatch_is_invalid(self) -> None:
        mismatch = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec3",
            preparation_id="wrong-preparation",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"ok": True},
        )
        result = self.service.verify(self.preparation, mismatch, integrity_id="result-integrity3")
        self.assertEqual(result.integrity_status, "INVALID")
        self.assertIsNone(result.result_fingerprint)

    def test_model_identity_mismatch_is_invalid(self) -> None:
        mismatch = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec4",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="other-expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"ok": True},
        )
        result = self.service.verify(self.preparation, mismatch, integrity_id="result-integrity4")
        self.assertEqual(result.integrity_status, "INVALID")

    def test_fingerprint_is_deterministic_for_equivalent_mappings(self) -> None:
        one = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec5",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"b": 2, "a": {"y": 1, "x": 3}},
        )
        two = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
            execution_id="retry-exec6",
            preparation_id="preparation1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED,
            observed_result={"a": {"x": 3, "y": 1}, "b": 2},
        )
        first = self.service.verify(self.preparation, one, integrity_id="result-integrity5")
        second = self.service.verify(self.preparation, two, integrity_id="result-integrity6")
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_nested_result_and_lineage_are_frozen(self) -> None:
        result = self.service.verify(
            self.preparation,
            self.attempt,
            integrity_id="result-integrity7",
            reasons={"cause": "checked"},
            lineage={"nested": {"source": "attempt"}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_source_artifacts_are_not_mutated(self) -> None:
        self.service.verify(self.preparation, self.attempt, integrity_id="result-integrity8")
        self.assertEqual(self.preparation.preparation_id, "preparation1")
        self.assertEqual(self.attempt.execution_id, "retry-exec1")

    def test_result_artifact_is_immutable(self) -> None:
        result = self.service.verify(self.preparation, self.attempt, integrity_id="result-integrity9")
        with self.assertRaises(AttributeError):
            result.integrity_status = "INVALID"

    def test_wrong_upstream_types_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.verify(object(), self.attempt, integrity_id="result-integrity10")
        with self.assertRaises(TypeError):
            self.service.verify(self.preparation, object(), integrity_id="result-integrity11")

    def test_integrity_artifact_type_is_explicit(self) -> None:
        result = self.service.verify(self.preparation, self.attempt, integrity_id="result-integrity12")
        self.assertIsInstance(result, EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity)

    def test_failed_attempt_with_empty_reason_cannot_exist(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult(
                execution_id="retry-exec13",
                preparation_id="preparation1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED,
                reason="   ",
            )

    def test_unsupported_status_fails_closed(self) -> None:
        invalid = object.__new__(EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult)
        for name, value in {
            "execution_id": "retry-exec14",
            "preparation_id": "preparation1",
            "environment_id": "env1",
            "expected_model_id": "expected",
            "observed_model_id": "observed",
            "status": "UNKNOWN",
            "observed_result": {"ok": True},
            "worker_id": None,
            "reason": None,
            "lineage": MappingProxyType({}),
        }.items():
            object.__setattr__(invalid, name, value)
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityError):
            self.service.verify(self.preparation, invalid, integrity_id="result-integrity13")


if __name__ == "__main__":
    unittest.main()
