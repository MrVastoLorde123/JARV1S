import unittest

from src.core.environment_world_model_rollback_repair_proposal import (
    EnvironmentWorldModelRollbackRepairProposal,
    EnvironmentWorldModelRollbackRepairProposalError,
    EnvironmentWorldModelRollbackRepairProposalService,
)
from src.core.environment_world_model_rollback_verification_decision import (
    EnvironmentWorldModelRollbackVerificationDecision,
)


class EnvironmentWorldModelRollbackRepairProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.accepted = EnvironmentWorldModelRollbackVerificationDecision(
            decision_id="vd1",
            environment_id="env1",
            verification_id="v1",
            expected_model_id="m0",
            observed_model_id="m0",
            decision="ACCEPT",
            reasons={"status": "verified"},
            lineage={"source": "verification"},
        )
        self.rejected = EnvironmentWorldModelRollbackVerificationDecision(
            decision_id="vd2",
            environment_id="env1",
            verification_id="v2",
            expected_model_id="m0",
            observed_model_id="m1",
            decision="REJECT",
            reasons={"status": "mismatch"},
            lineage={"source": "verification"},
        )
        self.service = EnvironmentWorldModelRollbackRepairProposalService()

    def test_accepted_verification_produces_no_repair(self) -> None:
        result = self.service.propose(self.accepted, proposal_id="rp1")
        self.assertEqual(result.recommendation, "NO_REPAIR")
        self.assertEqual(result.environment_id, "env1")

    def test_rejected_verification_produces_repair_proposal(self) -> None:
        result = self.service.propose(self.rejected, proposal_id="rp1")
        self.assertEqual(result.recommendation, "REPAIR")
        self.assertEqual(result.expected_model_id, "m0")
        self.assertEqual(result.observed_model_id, "m1")

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="rp1",
            lineage={"nested": {"source": "vd2"}},
        )
        self.assertEqual(result.proposal_id, "rp1")
        self.assertEqual(result.verification_decision_id, "vd2")
        self.assertEqual(result.lineage["nested"]["source"], "vd2")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="rp1",
            reasons={"status": "manual_review_required"},
        )
        self.assertEqual(result.reasons["status"], "manual_review_required")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.propose(
            self.rejected,
            proposal_id="rp1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_decision_is_not_mutated(self) -> None:
        result = self.service.propose(self.rejected, proposal_id="rp1")
        self.assertEqual(self.rejected.decision, "REJECT")
        self.assertEqual(result.verification_decision_id, self.rejected.decision_id)

    def test_repair_is_not_applied(self) -> None:
        result = self.service.propose(self.rejected, proposal_id="rp1")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_repair)

    def test_defer_decision_fails_closed(self) -> None:
        deferred = EnvironmentWorldModelRollbackVerificationDecision(
            decision_id="vd3",
            environment_id="env1",
            verification_id="v3",
            expected_model_id="m0",
            observed_model_id="m0",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairProposalError):
            self.service.propose(deferred, proposal_id="rp1")

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="rp1")


if __name__ == "__main__":
    unittest.main()
