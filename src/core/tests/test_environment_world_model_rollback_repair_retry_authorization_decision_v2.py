import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)
from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.next_at = datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc)
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service()
        self.retry = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="proposal1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            evaluated_at=self.now,
            next_eligible_at=self.next_at,
            reasons={"status": "eligible"},
            lineage={"source": "assessment"},
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id="feedback1",
            outcome_id="outcome1",
            assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE,
            retry_count=1,
            max_retries=3,
            eligible=True,
        )
        self.no_auth = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="proposal2",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="NO_AUTHORIZATION",
            evaluated_at=self.now,
            next_eligible_at=None,
            reasons={"status": "waiting"},
            lineage={"source": "assessment"},
            assessment_id="assessment2",
            evaluation_id="evaluation2",
            feedback_id="feedback2",
            outcome_id="outcome2",
            assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING,
            retry_count=1,
            max_retries=3,
            eligible=False,
        )

    def test_eligible_retry_produces_accept(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)

    def test_no_authorization_produces_reject(self) -> None:
        result = self.service.decide(self.no_auth, decision_id="decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_defer_artifact_is_representable(self) -> None:
        result = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2(
            decision_id="decision3",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id="evaluation1",
            feedback_id="feedback1",
            outcome_id="outcome1",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE.value,
            eligible=True,
            retry_count=1,
            max_retries=3,
            evaluated_at=self.now,
            next_eligible_at=self.next_at,
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.assertEqual(result.decision, "DEFER")

    def test_identity_and_timing_are_preserved(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision4")
        self.assertEqual(result.proposal_id, self.retry.proposal_id)
        self.assertEqual(result.assessment_id, self.retry.assessment_id)
        self.assertEqual(result.evaluation_id, self.retry.evaluation_id)
        self.assertEqual(result.feedback_id, self.retry.feedback_id)
        self.assertEqual(result.outcome_id, self.retry.outcome_id)
        self.assertEqual(result.next_eligible_at, self.next_at)

    def test_retry_bounds_are_preserved(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision5")
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(result.max_retries, 3)
        self.assertTrue(result.eligible)

    def test_reasons_and_lineage_are_frozen(self) -> None:
        result = self.service.decide(
            self.retry,
            decision_id="decision6",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_proposal_is_not_mutated(self) -> None:
        self.service.decide(self.retry, decision_id="decision7")
        self.assertEqual(self.retry.requested_action, "RETRY_REPAIR")
        self.assertTrue(self.retry.eligible)

    def test_retry_action_with_false_eligibility_fails_closed(self) -> None:
        invalid = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="proposal3",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            evaluated_at=self.now,
            next_eligible_at=None,
            reasons={},
            lineage={},
            assessment_id="assessment3",
            evaluation_id="evaluation3",
            feedback_id="feedback3",
            outcome_id="outcome3",
            assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE,
            retry_count=3,
            max_retries=3,
            eligible=False,
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error):
            self.service.decide(invalid, decision_id="decision8")

    def test_invalid_decision_id_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.service.decide(self.retry, decision_id=" ")

    def test_wrong_upstream_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision9")


if __name__ == "__main__":
    unittest.main()
