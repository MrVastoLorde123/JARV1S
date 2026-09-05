import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_authorization_decision import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_integrity import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityError,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityService,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="auth-proposal1",
            environment_id="env1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=True,
            evaluated_at="2026-09-05T20:00:00+00:00",
            next_eligible_at="2026-09-05T20:00:20+00:00",
            reasons={"status": "eligible"},
            lineage={"source": "eligibility"},
        )
        self.decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision1",
            environment_id="env1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            reasons={"status": "accepted"},
            lineage={"source": "proposal"},
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityService()

    def test_consistent_accepted_decision_is_valid(self) -> None:
        result = self.service.verify(self.proposal, self.decision, integrity_id="integrity1")
        self.assertEqual(result.integrity_status, "VALID")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.grants_execution_authority)
        self.assertFalse(result.authorizes_retry)

    def test_ineligible_retry_cannot_be_validly_accepted(self) -> None:
        proposal = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="auth-proposal2",
            environment_id="env1",
            eligibility_id="eligibility2",
            action_decision_id="action-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            eligible=False,
            evaluated_at="2026-09-05T20:00:00+00:00",
            next_eligible_at=None,
            reasons={},
            lineage={},
        )
        decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision2",
            environment_id="env1",
            proposal_id="auth-proposal2",
            eligibility_id="eligibility2",
            action_decision_id="action-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            reasons={},
            lineage={},
        )
        result = self.service.verify(proposal, decision, integrity_id="integrity2")
        self.assertEqual(result.integrity_status, "INVALID")

    def test_rejected_no_authorization_is_valid(self) -> None:
        proposal = EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id="auth-proposal3",
            environment_id="env1",
            eligibility_id="eligibility3",
            action_decision_id="action-decision3",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="NO_AUTHORIZATION",
            eligible=False,
            evaluated_at="2026-09-05T20:00:00+00:00",
            next_eligible_at=None,
            reasons={},
            lineage={},
        )
        decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision3",
            environment_id="env1",
            proposal_id="auth-proposal3",
            eligibility_id="eligibility3",
            action_decision_id="action-decision3",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="NO_AUTHORIZATION",
            decision="REJECT",
            reasons={},
            lineage={},
        )
        result = self.service.verify(proposal, decision, integrity_id="integrity3")
        self.assertEqual(result.integrity_status, "VALID")

    def test_deferred_decision_produces_defer_integrity(self) -> None:
        decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision4",
            environment_id="env1",
            proposal_id="auth-proposal1",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        result = self.service.verify(self.proposal, decision, integrity_id="integrity4")
        self.assertEqual(result.integrity_status, "DEFER")

    def test_identity_or_action_mismatch_is_invalid(self) -> None:
        decision = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id="decision5",
            environment_id="env1",
            proposal_id="wrong-proposal",
            eligibility_id="eligibility1",
            action_decision_id="action-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            requested_action="RETRY_REPAIR",
            decision="ACCEPT",
            reasons={},
            lineage={},
        )
        result = self.service.verify(self.proposal, decision, integrity_id="integrity5")
        self.assertEqual(result.integrity_status, "INVALID")

    def test_reasons_and_lineage_are_preserved_and_frozen(self) -> None:
        result = self.service.verify(
            self.proposal,
            self.decision,
            integrity_id="integrity6",
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.reasons["cause"], "validated")
        self.assertEqual(result.lineage["nested"]["source"], "test")
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"
        self.assertIsInstance(result.reasons, MappingProxyType)

    def test_result_is_immutable(self) -> None:
        result = self.service.verify(self.proposal, self.decision, integrity_id="integrity7")
        with self.assertRaises(AttributeError):
            result.integrity_status = "INVALID"

    def test_source_artifacts_are_not_mutated(self) -> None:
        self.service.verify(self.proposal, self.decision, integrity_id="integrity8")
        self.assertEqual(self.proposal.requested_action, "RETRY_REPAIR")
        self.assertEqual(self.decision.decision, "ACCEPT")

    def test_wrong_upstream_types_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.verify(object(), self.decision, integrity_id="integrity9")
        with self.assertRaises(TypeError):
            self.service.verify(self.proposal, object(), integrity_id="integrity10")

    def test_invalid_integrity_artifact_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity(
                integrity_id="integrity11",
                environment_id="env1",
                authorization_decision_id="decision1",
                proposal_id="auth-proposal1",
                eligibility_id="eligibility1",
                action_decision_id="action-decision1",
                requested_action="RETRY_REPAIR",
                decision="ACCEPT",
                proposal_eligible=True,
                integrity_status="UNKNOWN",
                reasons={},
                lineage={},
            )

    def test_unsupported_proposal_action_fails_closed(self) -> None:
        invalid = object.__new__(EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal)
        for name, value in {
            "proposal_id": "bad",
            "environment_id": "env1",
            "eligibility_id": "eligibility1",
            "action_decision_id": "action-decision1",
            "expected_model_id": "expected",
            "observed_model_id": "observed",
            "requested_action": "OTHER",
            "eligible": True,
            "evaluated_at": "2026-09-05T20:00:00+00:00",
            "next_eligible_at": None,
            "reasons": MappingProxyType({}),
            "lineage": MappingProxyType({}),
        }.items():
            object.__setattr__(invalid, name, value)
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityError):
            self.service.verify(invalid, self.decision, integrity_id="integrity12")


if __name__ == "__main__":
    unittest.main()
