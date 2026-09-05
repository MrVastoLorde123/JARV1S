import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_decision import (
    EnvironmentWorldModelRollbackRepairDecision,
    EnvironmentWorldModelRollbackRepairDecisionError,
    EnvironmentWorldModelRollbackRepairDecisionService,
)
from src.core.environment_world_model_rollback_repair_proposal import (
    EnvironmentWorldModelRollbackRepairProposal,
)


class EnvironmentWorldModelRollbackRepairDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = EnvironmentWorldModelRollbackRepairProposal(
            proposal_id="proposal1",
            environment_id="env1",
            verification_decision_id="decision1",
            expected_model_id="m0",
            observed_model_id="m1",
            recommendation="REPAIR",
            reasons={"status": "repair proposed"},
            lineage={"source": "proposal"},
        )
        self.service = EnvironmentWorldModelRollbackRepairDecisionService()

    def test_repair_proposal_produces_accept(self) -> None:
        result = self.service.decide(self.proposal, decision_id="repair-decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_repair)

    def test_no_repair_proposal_produces_reject(self) -> None:
        proposal = EnvironmentWorldModelRollbackRepairProposal(
            proposal_id="proposal2",
            environment_id="env1",
            verification_decision_id="decision2",
            expected_model_id="m0",
            observed_model_id="m0",
            recommendation="NO_REPAIR",
            reasons={},
            lineage={},
        )
        result = self.service.decide(proposal, decision_id="repair-decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_identity_and_lineage_are_preserved(self) -> None:
        lineage = {"nested": {"source": "proposal"}}
        result = self.service.decide(
            self.proposal,
            decision_id="repair-decision1",
            lineage=lineage,
        )
        self.assertEqual(result.proposal_id, "proposal1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "m0")
        self.assertEqual(result.observed_model_id, "m1")
        self.assertEqual(result.lineage["nested"]["source"], "proposal")

    def test_reasons_are_preserved(self) -> None:
        reasons = {"cause": "observation mismatch"}
        result = self.service.decide(
            self.proposal,
            decision_id="repair-decision1",
            reasons=reasons,
        )
        self.assertEqual(result.reasons["cause"], "observation mismatch")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.proposal,
            decision_id="repair-decision1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_proposal_is_not_mutated(self) -> None:
        before = (
            self.proposal.recommendation,
            self.proposal.reasons,
            self.proposal.lineage,
        )
        self.service.decide(self.proposal, decision_id="repair-decision1")
        after = (
            self.proposal.recommendation,
            self.proposal.reasons,
            self.proposal.lineage,
        )
        self.assertEqual(before, after)

    def test_unsupported_recommendation_fails_closed(self) -> None:
        invalid = object.__new__(EnvironmentWorldModelRollbackRepairProposal)
        object.__setattr__(invalid, "proposal_id", "proposal-invalid")
        object.__setattr__(invalid, "environment_id", "env1")
        object.__setattr__(invalid, "verification_decision_id", "decision1")
        object.__setattr__(invalid, "expected_model_id", "m0")
        object.__setattr__(invalid, "observed_model_id", "m1")
        object.__setattr__(invalid, "recommendation", "REVIEW")
        object.__setattr__(invalid, "reasons", MappingProxyType({}))
        object.__setattr__(invalid, "lineage", MappingProxyType({}))
        with self.assertRaises(EnvironmentWorldModelRollbackRepairDecisionError):
            self.service.decide(invalid, decision_id="repair-decision1")

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="repair-decision1")


if __name__ == "__main__":
    unittest.main()
