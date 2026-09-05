import unittest

from src.core.environment_world_model_rollback_repair_follow_up_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpProposal,
    EnvironmentWorldModelRollbackRepairFollowUpProposalError,
    EnvironmentWorldModelRollbackRepairFollowUpProposalService,
)
from src.core.environment_world_model_rollback_repair_verification_decision import (
    EnvironmentWorldModelRollbackRepairVerificationDecision,
)


class EnvironmentWorldModelRollbackRepairFollowUpProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.accepted = EnvironmentWorldModelRollbackRepairVerificationDecision(
            decision_id="decision1",
            environment_id="env1",
            verification_id="verification1",
            expected_model_id="expected",
            observed_model_id="expected",
            decision="ACCEPT",
            reasons={"status": "verified"},
            lineage={"source": "verification"},
        )
        self.rejected = EnvironmentWorldModelRollbackRepairVerificationDecision(
            decision_id="decision2",
            environment_id="env1",
            verification_id="verification2",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="REJECT",
            reasons={"status": "unverified"},
            lineage={"source": "verification"},
        )
        self.service = EnvironmentWorldModelRollbackRepairFollowUpProposalService()

    def test_rejected_verification_produces_follow_up(self) -> None:
        result = self.service.propose(self.rejected, proposal_id="proposal1")
        self.assertEqual(result.recommendation, "FOLLOW_UP")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_follow_up)

    def test_accepted_verification_produces_no_follow_up(self) -> None:
        result = self.service.propose(self.accepted, proposal_id="proposal2")
        self.assertEqual(result.recommendation, "NO_FOLLOW_UP")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_follow_up)

    def test_defer_decision_fails_closed(self) -> None:
        deferred = EnvironmentWorldModelRollbackRepairVerificationDecision(
            decision_id="decision3",
            environment_id="env1",
            verification_id="verification3",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairFollowUpProposalError):
            self.service.propose(deferred, proposal_id="proposal3")

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="proposal4",
            lineage={"nested": {"decision": "decision2"}},
        )
        self.assertEqual(result.proposal_id, "proposal4")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.verification_decision_id, "verification2")
        self.assertEqual(result.lineage["nested"]["decision"], "decision2")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="proposal5",
            reasons={"cause": "observed state diverged"},
        )
        self.assertEqual(result.reasons["cause"], "observed state diverged")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="proposal6",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_decision_is_not_mutated(self) -> None:
        self.service.propose(self.rejected, proposal_id="proposal7")
        self.assertEqual(self.rejected.decision, "REJECT")
        self.assertEqual(self.rejected.verification_id, "verification2")

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="proposal8")


if __name__ == "__main__":
    unittest.main()
