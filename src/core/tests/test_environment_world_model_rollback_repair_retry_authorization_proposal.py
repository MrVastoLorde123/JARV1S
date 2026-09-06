import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService,
)
from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment,
    EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.next_at = datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc)
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService()
        self.eligible = self._assessment(
            assessment_id="assessment1",
            status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE,
            retry_count=1,
            next_eligible_at=self.next_at,
        )
        self.waiting = self._assessment(
            assessment_id="assessment2",
            status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING,
            retry_count=1,
            next_eligible_at=self.next_at,
        )
        self.ineligible = self._assessment(
            assessment_id="assessment3",
            status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE,
            retry_count=3,
            next_eligible_at=None,
        )

    def _assessment(
        self,
        *,
        assessment_id: str,
        status: EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
        retry_count: int,
        next_eligible_at: datetime | None,
    ) -> EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment:
        return EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment(
            assessment_id=assessment_id,
            evaluation_id=f"evaluation-{assessment_id}",
            feedback_id=f"feedback-{assessment_id}",
            outcome_id=f"outcome-{assessment_id}",
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION,
            retry_count=retry_count,
            max_retries=3,
            evaluated_at=self.now,
            next_eligible_at=next_eligible_at,
            status=status,
            reasons={"status": status.value.lower()},
            lineage={"source": "assessment"},
        )

    def test_eligible_assessment_produces_retry_authorization_proposal(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal1")
        self.assertEqual(result.requested_action, "RETRY_REPAIR")
        self.assertEqual(result.assessment_status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE)
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)
        self.assertFalse(result.schedules_retry)

    def test_waiting_assessment_produces_no_authorization(self) -> None:
        result = self.service.propose(self.waiting, proposal_id="proposal2")
        self.assertEqual(result.requested_action, "NO_AUTHORIZATION")
        self.assertEqual(result.assessment_status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING)
        self.assertEqual(result.next_eligible_at, self.next_at)

    def test_not_eligible_assessment_produces_no_authorization(self) -> None:
        result = self.service.propose(self.ineligible, proposal_id="proposal3")
        self.assertEqual(result.requested_action, "NO_AUTHORIZATION")
        self.assertEqual(result.assessment_status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE)
        self.assertIsNone(result.next_eligible_at)

    def test_identity_and_retry_bounds_are_preserved(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal4")
        self.assertEqual(result.assessment_id, self.eligible.assessment_id)
        self.assertEqual(result.evaluation_id, self.eligible.evaluation_id)
        self.assertEqual(result.feedback_id, self.eligible.feedback_id)
        self.assertEqual(result.outcome_id, self.eligible.outcome_id)
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(result.max_retries, 3)
        self.assertEqual(result.evaluated_at, self.now)

    def test_reasons_and_lineage_are_preserved_and_frozen(self) -> None:
        result = self.service.propose(
            self.eligible,
            proposal_id="proposal5",
            reasons={"cause": "bounded-policy"},
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.reasons["cause"], "bounded-policy")
        self.assertEqual(result.lineage["nested"]["source"], "test")
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["cause"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"

    def test_source_assessment_is_not_mutated(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal6")
        self.assertEqual(result.assessment_id, self.eligible.assessment_id)
        self.assertEqual(self.eligible.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE)

    def test_wrong_upstream_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="proposal7")

    def test_empty_proposal_id_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.service.propose(self.eligible, proposal_id=" ")

    def test_artifact_rejects_unknown_requested_action(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
                proposal_id="proposal8",
                assessment_id="assessment1",
                evaluation_id="evaluation1",
                feedback_id="feedback1",
                outcome_id="outcome1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                assessment_status=EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE,
                requested_action="AUTHORIZE",
                retry_count=1,
                max_retries=3,
                evaluated_at=self.now,
                next_eligible_at=None,
                reasons={},
                lineage={},
            )

    def test_artifact_rejects_invalid_assessment_status(self) -> None:
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
                proposal_id="proposal9",
                assessment_id="assessment1",
                evaluation_id="evaluation1",
                feedback_id="feedback1",
                outcome_id="outcome1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                assessment_status="ELIGIBLE",
                requested_action="RETRY_REPAIR",
                retry_count=1,
                max_retries=3,
                evaluated_at=self.now,
                next_eligible_at=None,
                reasons={},
                lineage={},
            )


if __name__ == "__main__":
    unittest.main()
