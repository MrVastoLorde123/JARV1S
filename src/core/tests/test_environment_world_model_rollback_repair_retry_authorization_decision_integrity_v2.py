import unittest
from datetime import datetime, timezone

from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal
from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service
from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus
from src.core.environment_world_model_rollback_repair_retry_authorization_decision_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Service,
)


class M23_51IntegrityTests(unittest.TestCase):
    def setUp(self):
        now = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.proposal = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="p1", environment_id="env1", expected_model_id="expected", observed_model_id="observed",
            requested_action="RETRY_REPAIR", evaluated_at=now, next_eligible_at=None,
            assessment_id="a1", evaluation_id="e1", feedback_id="f1", outcome_id="o1",
            assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE,
            retry_count=1, max_retries=3, eligible=True, reasons={}, lineage={},
        )
        self.decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service().decide(self.proposal, decision_id="d1")
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Service()

    def test_valid_pair_is_valid(self):
        result = self.service.verify(self.proposal, self.decision, integrity_id="i1")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID)

    def test_identity_mismatch_is_invalid(self):
        bad = self.decision.__class__(**{**self.decision.__dict__, "proposal_id": "other"})
        result = self.service.verify(self.proposal, bad, integrity_id="i2")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.INVALID)

    def test_action_mismatch_is_invalid(self):
        bad = self.decision.__class__(**{**self.decision.__dict__, "requested_action": "NO_AUTHORIZATION"})
        result = self.service.verify(self.proposal, bad, integrity_id="i3")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.INVALID)

    def test_accepted_without_eligibility_is_invalid(self):
        bad_proposal = self.proposal.__class__(**{**self.proposal.__dict__, "eligible": False, "requested_action": "RETRY_REPAIR"})
        bad_decision = self.decision.__class__(**{**self.decision.__dict__, "eligible": False})
        result = self.service.verify(bad_proposal, bad_decision, integrity_id="i4")
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.INVALID)

    def test_result_is_immutable_and_advisory(self):
        result = self.service.verify(self.proposal, self.decision, integrity_id="i5", lineage={"nested": {"x": "y"}})
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["x"] = "z"


if __name__ == "__main__":
    unittest.main()
