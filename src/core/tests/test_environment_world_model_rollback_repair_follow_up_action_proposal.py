import unittest

from src.core.environment_world_model_rollback_repair_follow_up_action_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpActionProposal,
    EnvironmentWorldModelRollbackRepairFollowUpActionProposalError,
    EnvironmentWorldModelRollbackRepairFollowUpActionProposalService,
)
from src.core.environment_world_model_rollback_repair_follow_up_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpDecision,
)


class EnvironmentWorldModelRollbackRepairFollowUpActionProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.accept = EnvironmentWorldModelRollbackRepairFollowUpDecision(
            decision_id="decision1",
            environment_id="env1",
            proposal_id="follow-up1",
            verification_decision_id="verification1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="ACCEPT",
            reasons={"status": "accept"},
            lineage={"source": "decision"},
        )
        self.reject = EnvironmentWorldModelRollbackRepairFollowUpDecision(
            decision_id="decision2",
            environment_id="env1",
            proposal_id="follow-up2",
            verification_decision_id="verification2",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="REJECT",
            reasons={"status": "reject"},
            lineage={"source": "decision"},
        )
        self.service = EnvironmentWorldModelRollbackRepairFollowUpActionProposalService()

    def test_accepted_decision_produces_retry_repair(self) -> None:
        result = self.service.propose(self.accept, proposal_id="action1")
        self.assertEqual(result.action, "RETRY_REPAIR")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.executes_action)

    def test_rejected_decision_produces_no_action(self) -> None:
        result = self.service.propose(self.reject, proposal_id="action2")
        self.assertEqual(result.action, "NO_ACTION")
        self.assertFalse(result.executes_action)

    def test_defer_decision_fails_closed(self) -> None:
        deferred = EnvironmentWorldModelRollbackRepairFollowUpDecision(
            decision_id="decision3",
            environment_id="env1",
            proposal_id="follow-up3",
            verification_decision_id="verification3",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairFollowUpActionProposalError):
            self.service.propose(deferred, proposal_id="action3")

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.propose(
            self.accept,
            proposal_id="action1",
            lineage={"nested": {"source": "decision"}},
        )
        self.assertEqual(result.proposal_id, "action1")
        self.assertEqual(result.follow_up_decision_id, "decision1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertEqual(result.lineage["nested"]["source"], "decision")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.propose(
            self.accept,
            proposal_id="action1",
            reasons={"why": "bounded retry may restore expected state"},
        )
        self.assertEqual(
            result.reasons["why"],
            "bounded retry may restore expected state",
        )

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.propose(
            self.accept,
            proposal_id="action1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_decision_is_not_mutated(self) -> None:
        result = self.service.propose(self.accept, proposal_id="action1")
        self.assertEqual(self.accept.decision, "ACCEPT")
        self.assertEqual(self.accept.proposal_id, "follow-up1")
        self.assertEqual(result.follow_up_decision_id, self.accept.decision_id)

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="action1")

    def test_action_artifact_rejects_unsupported_action_and_remains_advisory(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairFollowUpActionProposal(
                proposal_id="action1",
                environment_id="env1",
                follow_up_decision_id="decision1",
                expected_model_id="expected",
                observed_model_id="observed",
                action="EXECUTE",
                reasons={},
                lineage={},
            )
        artifact = EnvironmentWorldModelRollbackRepairFollowUpActionProposal(
            proposal_id="action2",
            environment_id="env1",
            follow_up_decision_id="decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            action="RETRY_REPAIR",
            reasons={},
            lineage={},
        )
        self.assertTrue(artifact.is_advisory_only)
        self.assertFalse(artifact.executes_action)


if __name__ == "__main__":
    unittest.main()
