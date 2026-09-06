"""M23.54 tests: result integrity for v2 retry execution attempts."""

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Service,
)


class M23_54ExecutionResultIntegrityV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.attempt = EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result(
            execution_id="execution1",
            preparation_id="preparation1",
            environment_id="env1",
            authorization_decision_id="decision1",
            authorization_integrity_id="auth-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id="feedback1",
            outcome_id="outcome1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            eligible=True,
            status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED,
            observed_result={"repair": {"ok": True}},
            worker_id="worker1",
            lineage={"source": {"stage": "m23.53"}},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Service()

    def test_completed_attempt_gets_deterministic_fingerprint(self) -> None:
        result = self.service.verify(self.attempt, integrity_id="result-integrity1")
        again = self.service.verify(self.attempt, integrity_id="result-integrity2")
        self.assertEqual(result.integrity_status, "VALID")
        self.assertIsNotNone(result.result_fingerprint)
        self.assertEqual(result.result_fingerprint, again.result_fingerprint)
        self.assertIsNone(result.failure_reason)

    def test_failed_attempt_preserves_reason_without_fingerprint(self) -> None:
        attempt = self.attempt.__class__(
            **{
                **self.attempt.__dict__,
                "status": EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED,
                "observed_result": None,
                "failure_reason": "repair failed",
            }
        )
        result = self.service.verify(attempt, integrity_id="result-integrity2")
        self.assertEqual(result.integrity_status, "VALID")
        self.assertIsNone(result.result_fingerprint)
        self.assertEqual(result.failure_reason, "repair failed")

    def test_lineage_and_identities_are_preserved(self) -> None:
        result = self.service.verify(self.attempt, integrity_id="result-integrity3")
        self.assertEqual(result.execution_id, "execution1")
        self.assertEqual(result.preparation_id, "preparation1")
        self.assertEqual(result.decision_id, "decision1")
        self.assertEqual(result.integrity_decision_id, "auth-integrity1")
        self.assertEqual(result.proposal_id, "proposal1")
        self.assertEqual(result.assessment_id, "assessment1")
        self.assertEqual(result.evaluation_id, "evaluation1")
        self.assertEqual(result.feedback_id, "feedback1")
        self.assertEqual(result.outcome_id, "outcome1")

    def test_invalid_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.verify(object(), integrity_id="result-integrity4")

    def test_result_is_immutable_and_advisory(self) -> None:
        result = self.service.verify(
            self.attempt,
            integrity_id="result-integrity5",
            lineage={"nested": {"items": ["x"]}},
        )
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.mutates_persistence)


if __name__ == "__main__":
    unittest.main()
