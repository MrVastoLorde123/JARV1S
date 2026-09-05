import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService,
)
from src.core.environment_world_model_rollback_repair_retry_eligibility import (
    EnvironmentWorldModelRollbackRepairRetryEligibility,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService()
        self.eligible = EnvironmentWorldModelRollbackRepairRetryEligibility(
            eligibility_id="eligibility1",
            environment_id="env1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            retry_count=1,
            max_retries=3,
            backoff_seconds=20.0,
            evaluated_at=self.now,
            next_eligible_at=datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc),
            eligible=True,
            reasons={"status": "eligible"},
            lineage={"source": "eligibility"},
        )
        self.ineligible = EnvironmentWorldModelRollbackRepairRetryEligibility(
            eligibility_id="eligibility2",
            environment_id="env1",
            action_decision_id="action-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            retry_count=3,
            max_retries=3,
            backoff_seconds=0.0,
            evaluated_at=self.now,
            next_eligible_at=None,
            eligible=False,
            reasons={"status": "limit"},
            lineage={},
        )

    def test_eligible_retry_produces_retry_authorization_proposal(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal1")
        self.assertEqual(result.requested_action, "RETRY_REPAIR")
        self.assertTrue(result.eligible)
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)

    def test_ineligible_retry_produces_no_authorization(self) -> None:
        result = self.service.propose(self.ineligible, proposal_id="proposal2")
        self.assertEqual(result.requested_action, "NO_AUTHORIZATION")
        self.assertFalse(result.eligible)
        self.assertIsNone(result.next_eligible_at)

    def test_identity_and_timing_are_preserved(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal3")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.eligibility_id, "eligibility1")
        self.assertEqual(result.action_decision_id, "action-decision1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertEqual(result.evaluated_at, self.now)
        self.assertEqual(
            result.next_eligible_at,
            datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc),
        )

    def test_reasons_and_lineage_are_preserved(self) -> None:
        result = self.service.propose(
            self.eligible,
            proposal_id="proposal4",
            reasons={"cause": "bounded-policy"},
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.reasons["cause"], "bounded-policy")
        self.assertEqual(result.lineage["nested"]["source"], "test")

    def test_result_evidence_is_recursively_immutable(self) -> None:
        result = self.service.propose(
            self.eligible,
            proposal_id="proposal5",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)
        self.assertIsInstance(result.reasons, MappingProxyType)

    def test_source_eligibility_is_not_mutated(self) -> None:
        result = self.service.propose(self.eligible, proposal_id="proposal6")
        self.assertTrue(self.eligible.eligible)
        self.assertEqual(result.eligibility_id, self.eligible.eligibility_id)

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
                environment_id="env1",
                eligibility_id="eligibility1",
                action_decision_id="action-decision1",
                expected_model_id="expected",
                observed_model_id="observed",
                requested_action="AUTHORIZE",
                eligible=True,
                evaluated_at=self.now,
                next_eligible_at=None,
                reasons={},
                lineage={},
            )


if __name__ == "__main__":
    unittest.main()
