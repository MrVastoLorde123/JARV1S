import unittest

from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2,
)
from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2,
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error,
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service,
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)


class M23_55OutcomeClassificationV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service()
        self.integrity = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id="result-integrity1",
            execution_id="execution1",
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_decision_id="decision-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id="feedback1",
            outcome_id=None,
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED,
            integrity_status="VALID",
            result_fingerprint="abc123",
            worker_id="worker1",
        )

    def test_completed_integrity_classifies_as_success_and_preserves_v2_chain(self) -> None:
        result = self.service.classify(self.integrity, outcome_id="outcome1")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS)
        self.assertEqual(result.result_fingerprint, "abc123")
        self.assertEqual(result.decision_id, "decision1")
        self.assertEqual(result.integrity_decision_id, "decision-integrity1")
        self.assertEqual(result.proposal_id, "proposal1")
        self.assertEqual(result.assessment_id, "assessment1")
        self.assertEqual(result.evaluation_id, "evaluation1")
        self.assertEqual(result.feedback_id, "feedback1")

    def test_failed_integrity_classifies_as_failure_and_preserves_reason(self) -> None:
        failed = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id="result-integrity2",
            execution_id="execution2",
            preparation_id="preparation2",
            decision_id="decision2",
            integrity_decision_id="decision-integrity2",
            proposal_id="proposal2",
            assessment_id="assessment2",
            evaluation_id="evaluation2",
            feedback_id="feedback2",
            outcome_id=None,
            environment_id="env2",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED,
            integrity_status="VALID",
            failure_reason="provider unavailable",
            worker_id="worker2",
        )
        result = self.service.classify(failed, outcome_id="outcome2")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE)
        self.assertEqual(result.failure_reason, "provider unavailable")
        self.assertIsNone(result.result_fingerprint)

    def test_invalid_integrity_cannot_be_classified(self) -> None:
        invalid = EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id="bad-integrity",
            execution_id="execution3",
            preparation_id="preparation3",
            decision_id="decision3",
            integrity_decision_id="decision-integrity3",
            proposal_id="proposal3",
            assessment_id=None,
            evaluation_id=None,
            feedback_id=None,
            outcome_id=None,
            environment_id="env3",
            expected_model_id="expected",
            observed_model_id="observed",
            attempt_status=EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED,
            integrity_status="INVALID",
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error):
            self.service.classify(invalid, outcome_id="outcome3")

    def test_outcome_is_immutable_and_advisory(self) -> None:
        result = self.service.classify(
            self.integrity,
            outcome_id="outcome4",
            lineage={"nested": {"source": "result-integrity"}},
        )
        with self.assertRaises(AttributeError):
            result.status = EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"
        self.assertTrue(result.is_observational)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.mutates_persistence)

    def test_source_integrity_is_not_mutated_and_id_is_required(self) -> None:
        with self.assertRaises(ValueError):
            self.service.classify(self.integrity, outcome_id="")
        self.service.classify(self.integrity, outcome_id="outcome5")
        self.assertEqual(self.integrity.integrity_id, "result-integrity1")
        self.assertEqual(self.integrity.integrity_status, "VALID")
        self.assertIsNone(self.integrity.outcome_id)


if __name__ == "__main__":
    unittest.main()
