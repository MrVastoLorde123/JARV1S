import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_repair_application import (
    EnvironmentWorldModelRollbackRepairApplication,
)
from src.core.environment_world_model_rollback_repair_verification import (
    EnvironmentWorldModelRollbackRepairVerificationService,
    EnvironmentWorldModelRollbackRepairVerificationError,
)


class EnvironmentWorldModelRollbackRepairVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed_bad = EnvironmentWorldModel(
            model_id="observed",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 1}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-observed",),
            qualification_ids=("q-observed",),
            provenance_ids=("p-observed",),
            readiness_id="r-observed",
            source_bundle_id="b-observed",
            lineage={"source": "observed"},
        )
        self.expected = EnvironmentWorldModel(
            model_id="expected",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 4}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-expected",),
            qualification_ids=("q-expected",),
            provenance_ids=("p-expected",),
            readiness_id="r-expected",
            source_bundle_id="b-expected",
            lineage={"source": "expected"},
        )
        self.application = EnvironmentWorldModelRollbackRepairApplication(
            application_id="application1",
            environment_id="env1",
            previous_model_id="observed",
            expected_model_id="expected",
            resulting_model_id="expected",
            decision_id="decision1",
            applied=True,
            reasons={"status": "repair"},
            lineage={"source": "application"},
        )
        self.service = EnvironmentWorldModelRollbackRepairVerificationService()

    def test_matching_result_is_verified(self) -> None:
        result = self.service.verify(
            self.application,
            self.expected,
            verification_id="verification1",
        )
        self.assertTrue(result.verified)
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "expected")

    def test_mismatched_observed_model_is_not_verified(self) -> None:
        result = self.service.verify(
            self.application,
            self.observed_bad,
            verification_id="verification1",
        )
        self.assertFalse(result.verified)
        self.assertEqual(result.observed_model_id, "observed")

    def test_unapplied_result_is_not_verified(self) -> None:
        application = EnvironmentWorldModelRollbackRepairApplication(
            application_id="application2",
            environment_id="env1",
            previous_model_id="observed",
            expected_model_id="expected",
            resulting_model_id="observed",
            decision_id="decision2",
            applied=False,
            reasons={},
            lineage={},
        )
        result = self.service.verify(
            application,
            self.observed_bad,
            verification_id="verification2",
        )
        self.assertFalse(result.verified)

    def test_environment_identity_must_match(self) -> None:
        foreign = EnvironmentWorldModel(
            model_id="foreign",
            environment_id="env2",
            state_by_domain={},
            represented_domains=(),
            missing_domains=(),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r2",
            source_bundle_id="b2",
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairVerificationError):
            self.service.verify(self.application, foreign, verification_id="verification1")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.verify(
            self.application,
            self.expected,
            verification_id="verification1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_sources_are_not_mutated(self) -> None:
        application = self.application
        observed = self.observed_bad
        expected = self.expected
        self.service.verify(application, expected, verification_id="verification1")
        self.assertEqual(application.resulting_model_id, "expected")
        self.assertEqual(observed.model_id, "observed")
        self.assertEqual(expected.model_id, "expected")

    def test_truth_and_authorization_properties_are_false(self) -> None:
        result = self.service.verify(
            self.application,
            self.expected,
            verification_id="verification1",
        )
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.is_authorization)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.verify(object(), self.expected, verification_id="verification1")
        with self.assertRaises(TypeError):
            self.service.verify(self.application, object(), verification_id="verification1")


if __name__ == "__main__":
    unittest.main()
