import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_follow_up_action_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpActionDecision,
    EnvironmentWorldModelRollbackRepairFollowUpActionDecisionError,
    EnvironmentWorldModelRollbackRepairFollowUpActionDecisionService,
)
from src.core.environment_world_model_rollback_repair_follow_up_action_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpActionProposal,
)


class EnvironmentWorldModelRollbackRepairFollowUpActionDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = EnvironmentWorldModelRollbackRepairFollowUpActionProposal(
            proposal_id="action-proposal1",
            environment_id="env1",
            follow_up_decision_id="follow-up-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            action="RETRY_REPAIR",
            reasons={"status": "retry"},
            lineage={"source": "proposal"},
        )
        self.service = EnvironmentWorldModelRollbackRepairFollowUpActionDecisionService()

    def test_retry_repair_proposal_produces_accept(self) -> None:
        result = self.service.decide(self.proposal, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_execution)
        self.assertFalse(result.executes_action)

    def test_no_action_proposal_produces_reject(self) -> None:
        proposal = EnvironmentWorldModelRollbackRepairFollowUpActionProposal(
            proposal_id="action-proposal2",
            environment_id="env1",
            follow_up_decision_id="follow-up-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            action="NO_ACTION",
            reasons={},
            lineage={},
        )
        result = self.service.decide(proposal, decision_id="decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_defer_decision_artifact_is_supported_but_not_fabricated(self) -> None:
        artifact = EnvironmentWorldModelRollbackRepairFollowUpActionDecision(
            decision_id="decision3",
            environment_id="env1",
            proposal_id="action-proposal1",
            follow_up_decision_id="follow-up-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.assertEqual(artifact.decision, "DEFER")
        with self.assertRaises(EnvironmentWorldModelRollbackRepairFollowUpActionDecisionError):
            invalid = object.__new__(EnvironmentWorldModelRollbackRepairFollowUpActionProposal)
            object.__setattr__(invalid, "proposal_id", "bad")
            object.__setattr__(invalid, "environment_id", "env1")
            object.__setattr__(invalid, "follow_up_decision_id", "follow-up-decision1")
            object.__setattr__(invalid, "expected_model_id", "expected")
            object.__setattr__(invalid, "observed_model_id", "observed")
            object.__setattr__(invalid, "action", "REVIEW")
            object.__setattr__(invalid, "reasons", MappingProxyType({}))
            object.__setattr__(invalid, "lineage", MappingProxyType({}))
            self.service.decide(invalid, decision_id="decision4")

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="decision5",
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.proposal_id, "action-proposal1")
        self.assertEqual(result.follow_up_decision_id, "follow-up-decision1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertEqual(result.lineage["nested"]["source"], "test")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="decision6",
            reasons={"cause": "verification-failed"},
        )
        self.assertEqual(result.reasons["cause"], "verification-failed")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.proposal,
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
        result = self.service.decide(self.proposal, decision_id="decision8")
        self.assertEqual(self.proposal.action, "RETRY_REPAIR")
        self.assertEqual(result.proposal_id, self.proposal.proposal_id)

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision9")


if __name__ == "__main__":
    unittest.main()
