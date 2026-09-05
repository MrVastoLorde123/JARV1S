import unittest

from src.core.environment_world_model_rollback_repair_verification import (
    EnvironmentWorldModelRollbackRepairVerification,
)
from src.core.environment_world_model_rollback_repair_verification_decision import (
    EnvironmentWorldModelRollbackRepairVerificationDecision,
    EnvironmentWorldModelRollbackRepairVerificationDecisionService,
)


class EnvironmentWorldModelRollbackRepairVerificationDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verification = EnvironmentWorldModelRollbackRepairVerification(
            verification_id="verification1",
            environment_id="env1",
            application_id="application1",
            expected_model_id="expected",
            observed_model_id="expected",
            verified=True,
            reasons={"status": "verified"},
            lineage={"source": "verification"},
        )
        self.service = EnvironmentWorldModelRollbackRepairVerificationDecisionService()

    def test_verified_result_produces_accept(self) -> None:
        result = self.service.decide(self.verification, decision_id="decision1")
        self.assertEqual(result.decision, "ACCEPT")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_follow_up)

    def test_unverified_result_produces_reject(self) -> None:
        verification = EnvironmentWorldModelRollbackRepairVerification(
            verification_id="verification2",
            environment_id="env1",
            application_id="application1",
            expected_model_id="expected",
            observed_model_id="observed",
            verified=False,
            reasons={},
            lineage={},
        )
        result = self.service.decide(verification, decision_id="decision2")
        self.assertEqual(result.decision, "REJECT")

    def test_identity_and_lineage_are_preserved(self) -> None:
        lineage = {"nested": {"source": "verification"}}
        result = self.service.decide(
            self.verification,
            decision_id="decision3",
            lineage=lineage,
        )
        self.assertEqual(result.decision_id, "decision3")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.verification_id, "verification1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "expected")
        self.assertEqual(result.lineage["nested"]["source"], "verification")

    def test_reasons_are_preserved(self) -> None:
        reasons = {"status": "explicit"}
        result = self.service.decide(
            self.verification,
            decision_id="decision4",
            reasons=reasons,
        )
        self.assertEqual(result.reasons["status"], "explicit")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self.verification,
            decision_id="decision5",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_source_verification_is_not_mutated(self) -> None:
        source = self.verification
        result = self.service.decide(source, decision_id="decision6")
        self.assertEqual(source.verification_id, "verification1")
        self.assertTrue(source.verified)
        self.assertEqual(result.verification_id, source.verification_id)

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision7")

    def test_decision_artifact_supports_defer_but_service_does_not_fabricate_it(self) -> None:
        defer = EnvironmentWorldModelRollbackRepairVerificationDecision(
            decision_id="decision8",
            environment_id="env1",
            verification_id="verification1",
            expected_model_id="expected",
            observed_model_id="expected",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.assertEqual(defer.decision, "DEFER")
        result = self.service.decide(self.verification, decision_id="decision9")
        self.assertNotEqual(result.decision, "DEFER")


if __name__ == "__main__":
    unittest.main()
