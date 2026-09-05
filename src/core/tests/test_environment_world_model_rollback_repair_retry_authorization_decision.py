import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_decision import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionError,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionService,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        evaluated_at = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        next_eligible_at = datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc)
        self.retry = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="auth-proposal1",
            environment_id="env1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=True,
            evaluated_at=evaluated_at,
            next_eligible_at=next_eligible_at,
            reasons={"status": "eligible"},
            lineage={"source": "eligibility"},
        )
        self.no_auth = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="auth-proposal2",
            environment_id="env1",
            eligibility_id="eligibility2",
            action_decision_id="action-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="NO_AUTHORIZATION",
            eligible=False,
            evaluated_at=evaluated_at,
            next_eligible_at=None,
            reasons={},
            lineage={},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionService()

    def test_retry_authorization_proposal_produces_accept(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)

    def test_no_authorization_proposal_produces_reject(self) -> None:
        result = self.service.decide(self.no_auth, decision_id="decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_defer_decision_artifact_is_supported_but_not_fabricated(self) -> None:
        artifact = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision3",
            environment_id="env1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=True,
            evaluated_at=datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc),
            next_eligible_at=datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc),
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.assertEqual(artifact.decision, "DEFER")
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionError):
            invalid = object.__new__(EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal)
            object.__setattr__(invalid, "proposal_id", "bad")
            object.__setattr__(invalid, "environment_id", "env1")
            object.__setattr__(invalid, "eligibility_id", "eligibility1")
            object.__setattr__(invalid, "action_decision_id", "action-decision1")
            object.__setattr__(invalid, "expected_model_id", "expected")
            object.__setattr__(invalid, "observed_model_id", "observed")
            object.__setattr__(invalid, "requested_action", "OTHER")
            object.__setattr__(invalid, "eligible", True)
            object.__setattr__(invalid, "evaluated_at", datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc))
            object.__setattr__(invalid, "next_eligible_at", None)
            object.__setattr__(invalid, "reasons", MappingProxyType({}))
            object.__setattr__(invalid, "lineage", MappingProxyType({}))
            self.service.decide(invalid, decision_id="decision4")

    def test_identity_and_timing_are_preserved(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision5")
        self.assertEqual(result.proposal_id, "auth-proposal1")
        self.assertEqual(result.eligibility_id, "eligibility1")
        self.assertEqual(result.action_decision_id, "action-decision1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertTrue(result.eligible)
        self.assertEqual(result.evaluated_at, self.retry.evaluated_at)
        self.assertEqual(result.next_eligible_at, self.retry.next_eligible_at)

    def test_reasons_and_lineage_are_preserved(self) -> None:
        result = self.service.decide(
            self.retry,
            decision_id="decision6",
            reasons={"cause": "policy-approved"},
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.reasons["cause"], "policy-approved")
        self.assertEqual(result.lineage["nested"]["source"], "test")

    def test_result_evidence_is_recursively_immutable(self) -> None:
        result = self.service.decide(
            self.retry,
            decision_id="decision7",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)
        self.assertIsInstance(result.reasons, MappingProxyType)

    def test_source_proposal_is_not_mutated(self) -> None:
        result = self.service.decide(self.retry, decision_id="decision8")
        self.assertEqual(self.retry.requested_action, "RETRY_REPAIR")
        self.assertTrue(self.retry.eligible)
        self.assertEqual(result.proposal_id, self.retry.proposal_id)

    def test_wrong_upstream_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision9")


if __name__ == "__main__":
    unittest.main()
