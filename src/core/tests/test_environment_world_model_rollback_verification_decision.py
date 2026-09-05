import unittest

from src.core.environment_world_model_rollback_verification import (
    EnvironmentWorldModelRollbackVerification,
)
from src.core.environment_world_model_rollback_verification_decision import (
    EnvironmentWorldModelRollbackVerificationDecisionService,
)


class EnvironmentWorldModelRollbackVerificationDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EnvironmentWorldModelRollbackVerificationDecisionService()
        self.verified = EnvironmentWorldModelRollbackVerification(
            verification_id="verification1",
            environment_id="env1",
            application_id="app1",
            persistence_id="persist1",
            expected_model_id="m0",
            observed_model_id="m0",
            verified=True,
            reasons={"status": "matched"},
            lineage={"source": "verification"},
        )
        self.unverified = EnvironmentWorldModelRollbackVerification(
            verification_id="verification2",
            environment_id="env1",
            application_id="app1",
            persistence_id="persist2",
            expected_model_id="m0",
            observed_model_id="m1",
            verified=False,
            reasons={"status": "mismatch"},
            lineage={"source": "verification"},
        )

    def test_verified_result_produces_accept(self) -> None:
        result = self.service.decide(self.verified, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertEqual(result.verification_id, "verification1")

    def test_unverified_result_produces_reject(self) -> None:
        result = self.service.decide(self.unverified, decision_id="decision1")
        self.assertEqual(result.decision, "REJECT")
        self.assertEqual(result.observed_model_id, "m1")

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.decide(
            self.verified,
            decision_id="decision1",
            lineage={"verification": "verification1"},
        )
        self.assertEqual(result.decision_id, "decision1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "m0")
        self.assertEqual(result.lineage["verification"], "verification1")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.decide(
            self.verified,
            decision_id="decision1",
            reasons={"operator": "confirmed"},
        )
        self.assertEqual(result.reasons["operator"], "confirmed")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.verified,
            decision_id="decision1",
            reasons={"nested": {"value": "x"}},
            lineage={"items": ["a"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["items"] = ("b",)

    def test_source_verification_is_not_mutated(self) -> None:
        result = self.service.decide(self.verified, decision_id="decision1")
        self.assertEqual(self.verified.verified, True)
        self.assertEqual(self.verified.observed_model_id, "m0")
        self.assertEqual(result.verification_id, self.verified.verification_id)

    def test_decision_is_advisory_and_does_not_authorize_repair(self) -> None:
        result = self.service.decide(self.unverified, decision_id="decision1")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_repair)

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision1")


if __name__ == "__main__":
    unittest.main()
