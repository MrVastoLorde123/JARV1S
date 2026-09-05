import unittest

from src.core.environment_world_model_rollback_repair_follow_up_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpDecision,
    EnvironmentWorldModelRollbackRepairFollowUpDecisionService,
)
from src.core.environment_world_model_rollback_repair_follow_up_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpProposal,
)


class EnvironmentWorldModelRollbackRepairFollowUpDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = EnvironmentWorldModelRollbackRepairFollowUpProposal(
            proposal_id="proposal1",
            environment_id="env1",
            verification_decision_id="verification1",
            expected_model_id="expected",
            observed_model_id="observed",
            recommendation="FOLLOW_UP",
            reasons={"status": "follow-up"},
            lineage={"source": "proposal"},
        )
        self.service = EnvironmentWorldModelRollbackRepairFollowUpDecisionService()

    def test_follow_up_proposal_produces_accept(self) -> None:
        result = self.service.decide(self.proposal, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)

    def test_no_follow_up_proposal_produces_reject(self) -> None:
        proposal = EnvironmentWorldModelRollbackRepairFollowUpProposal(
            proposal_id="proposal2",
            environment_id="env1",
            verification_decision_id="verification1",
            expected_model_id="expected",
            observed_model_id="observed",
            recommendation="NO_FOLLOW_UP",
            reasons={},
            lineage={},
        )
        result = self.service.decide(proposal, decision_id="decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_defer_decision_artifact_is_supported_but_not_fabricated(self) -> None:
        result = EnvironmentWorldModelRollbackRepairFollowUpDecision(
            decision_id="decision3",
            environment_id="env1",
            proposal_id="proposal1",
            verification_decision_id="verification1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.assertEqual(result.decision, "DEFER")
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairFollowUpDecision(
                decision_id="bad",
                environment_id="env1",
                proposal_id="proposal1",
                verification_decision_id="verification1",
                expected_model_id="expected",
                observed_model_id="observed",
                decision="REVIEW",
            )

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="decision4",
            lineage={"nested": {"source": "proposal"}},
        )
        self.assertEqual(result.proposal_id, "proposal1")
        self.assertEqual(result.verification_decision_id, "verification1")
        self.assertEqual(result.lineage["nested"]["source"], "proposal")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="decision5",
            reasons={"reason": "user-review-required"},
        )
        self.assertEqual(result.reasons["reason"], "user-review-required")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="decision6",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_proposal_is_not_mutated(self) -> None:
        original = self.proposal
        self.service.decide(original, decision_id="decision7")
        self.assertEqual(original.recommendation, "FOLLOW_UP")
        self.assertEqual(original.proposal_id, "proposal1")

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision8")


if __name__ == "__main__":
    unittest.main()
