import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_decision_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_execution_preparation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Service,
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error,
)


class M23_52ExecutionPreparationV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluated_at = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.next_eligible_at = datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc)
        self.decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2(
            decision_id="decision-v2-1",
            proposal_id="proposal-v2-1",
            assessment_id="assessment-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            environment_id="env-1",
            expected_model_id="expected-1",
            observed_model_id="observed-1",
            requested_action="RETRY_REPAIR",
            assessment_status="ELIGIBLE",
            eligible=True,
            retry_count=1,
            max_retries=3,
            evaluated_at=self.evaluated_at,
            next_eligible_at=self.next_eligible_at,
            decision="ACCEPT",
            reasons={"status": "accepted"},
            lineage={"source": "proposal"},
        )
        self.integrity = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2(
            integrity_id="integrity-v2-1",
            proposal_id="proposal-v2-1",
            decision_id="decision-v2-1",
            status=EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID,
            reasons={"status": "valid"},
            lineage={"source": "decision"},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Service()

    def test_valid_pair_produces_inert_preparation(self) -> None:
        result = self.service.prepare(self.decision, self.integrity, preparation_id="prep-v2-1")
        self.assertEqual(result.preparation_id, "prep-v2-1")
        self.assertEqual(result.decision_id, "decision-v2-1")
        self.assertEqual(result.integrity_id, "integrity-v2-1")
        self.assertEqual(result.proposal_id, "proposal-v2-1")
        self.assertEqual(result.assessment_id, "assessment-1")
        self.assertEqual(result.evaluation_id, "evaluation-1")
        self.assertEqual(result.feedback_id, "feedback-1")
        self.assertEqual(result.outcome_id, "outcome-1")
        self.assertTrue(result.is_non_executing)
        self.assertFalse(result.execution_started)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.schedules_retry)
        self.assertFalse(result.reauthorizes_retry)
        self.assertFalse(result.mutates_persistence)

    def test_invalid_integrity_is_rejected(self) -> None:
        invalid = self.integrity.__class__(
            integrity_id="integrity-v2-invalid",
            proposal_id="proposal-v2-1",
            decision_id="decision-v2-1",
            status=EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.INVALID,
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error):
            self.service.prepare(self.decision, invalid, preparation_id="prep-v2-2")

    def test_identity_mismatch_is_rejected(self) -> None:
        mismatched = self.integrity.__class__(
            integrity_id="integrity-v2-mismatch",
            proposal_id="wrong-proposal",
            decision_id="decision-v2-1",
            status=EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID,
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error):
            self.service.prepare(self.decision, mismatched, preparation_id="prep-v2-3")

    def test_non_retry_decision_is_rejected(self) -> None:
        bad = self.decision.__class__(
            decision_id=self.decision.decision_id,
            proposal_id=self.decision.proposal_id,
            assessment_id=self.decision.assessment_id,
            evaluation_id=self.decision.evaluation_id,
            feedback_id=self.decision.feedback_id,
            outcome_id=self.decision.outcome_id,
            environment_id=self.decision.environment_id,
            expected_model_id=self.decision.expected_model_id,
            observed_model_id=self.decision.observed_model_id,
            requested_action="NO_AUTHORIZATION",
            assessment_status=self.decision.assessment_status,
            eligible=False,
            retry_count=self.decision.retry_count,
            max_retries=self.decision.max_retries,
            evaluated_at=self.decision.evaluated_at,
            next_eligible_at=self.decision.next_eligible_at,
            decision="REJECT",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error):
            self.service.prepare(bad, self.integrity, preparation_id="prep-v2-4")

    def test_result_and_inputs_remain_immutable(self) -> None:
        result = self.service.prepare(
            self.decision,
            self.integrity,
            preparation_id="prep-v2-5",
            reasons={"nested": {"state": "ready"}},
            lineage={"chain": {"decision": "decision-v2-1"}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["chain"] = "changed"
        self.assertEqual(self.decision.decision, "ACCEPT")
        self.assertEqual(self.integrity.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID)


if __name__ == "__main__":
    unittest.main()
