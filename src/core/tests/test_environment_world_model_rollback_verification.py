import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_application import (
    EnvironmentWorldModelRollbackApplication,
)
from src.core.environment_world_model_rollback_persistence import (
    EnvironmentWorldModelRollbackPersistence,
)
from src.core.environment_world_model_rollback_verification import (
    EnvironmentWorldModelRollbackVerificationError,
    EnvironmentWorldModelRollbackVerificationService,
)


class EnvironmentWorldModelRollbackVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.application = EnvironmentWorldModelRollbackApplication(
            application_id="app1",
            environment_id="env1",
            previous_model_id="m1",
            target_model_id="m0",
            decision_id="decision1",
            applied=True,
            resulting_model_id="m0",
            reasons={"status": "test"},
            lineage={"source": "application"},
        )
        self.persistence = EnvironmentWorldModelRollbackPersistence(
            persistence_id="persist1",
            environment_id="env1",
            application_id="app1",
            previous_model_id="m1",
            resulting_model_id="m0",
            persisted=True,
            reasons={"status": "test"},
            lineage={"source": "persistence"},
        )
        self.observed = EnvironmentWorldModel(
            model_id="m0",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 2}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx0",),
            qualification_ids=("q0",),
            provenance_ids=("p0",),
            readiness_id="r0",
            source_bundle_id="b0",
            lineage={"source": "observed"},
        )
        self.service = EnvironmentWorldModelRollbackVerificationService()

    def test_matching_persisted_result_is_verified(self) -> None:
        result = self.service.verify(
            self.application,
            self.persistence,
            self.observed,
            verification_id="verify1",
        )
        self.assertTrue(result.verified)
        self.assertEqual(result.expected_model_id, "m0")
        self.assertEqual(result.observed_model_id, "m0")

    def test_mismatched_observed_model_is_not_verified(self) -> None:
        different = EnvironmentWorldModel(
            model_id="m-other",
            environment_id="env1",
            state_by_domain={},
            represented_domains=(),
            missing_domains=("hardware", "software"),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r-other",
            source_bundle_id="b-other",
            lineage={},
        )
        result = self.service.verify(
            self.application,
            self.persistence,
            different,
            verification_id="verify1",
        )
        self.assertFalse(result.verified)
        self.assertEqual(result.expected_model_id, "m0")
        self.assertEqual(result.observed_model_id, "m-other")

    def test_unpersisted_result_is_not_verified(self) -> None:
        persistence = EnvironmentWorldModelRollbackPersistence(
            persistence_id="persist1",
            environment_id="env1",
            application_id="app1",
            previous_model_id="m1",
            resulting_model_id="m0",
            persisted=False,
            reasons={},
            lineage={},
        )
        result = self.service.verify(
            self.application,
            persistence,
            self.observed,
            verification_id="verify1",
        )
        self.assertFalse(result.verified)

    def test_identity_mismatch_is_rejected(self) -> None:
        persistence = EnvironmentWorldModelRollbackPersistence(
            persistence_id="persist2",
            environment_id="env1",
            application_id="different-app",
            previous_model_id="m1",
            resulting_model_id="m0",
            persisted=True,
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackVerificationError):
            self.service.verify(
                self.application,
                persistence,
                self.observed,
                verification_id="verify1",
            )

    def test_environment_mismatch_is_rejected(self) -> None:
        foreign = EnvironmentWorldModel(
            model_id="m0",
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
        with self.assertRaises(EnvironmentWorldModelRollbackVerificationError):
            self.service.verify(
                self.application,
                self.persistence,
                foreign,
                verification_id="verify1",
            )

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.verify(
            self.application,
            self.persistence,
            self.observed,
            verification_id="verify1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_sources_are_not_mutated(self) -> None:
        result = self.service.verify(
            self.application,
            self.persistence,
            self.observed,
            verification_id="verify1",
        )
        self.assertEqual(self.application.application_id, "app1")
        self.assertEqual(self.persistence.persistence_id, "persist1")
        self.assertEqual(result.observed_model_id, "m0")

    def test_truth_and_authorization_properties_are_false(self) -> None:
        result = self.service.verify(
            self.application,
            self.persistence,
            self.observed,
            verification_id="verify1",
        )
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.is_authorization)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.verify(object(), self.persistence, self.observed, verification_id="verify1")
        with self.assertRaises(TypeError):
            self.service.verify(self.application, object(), self.observed, verification_id="verify1")
        with self.assertRaises(TypeError):
            self.service.verify(self.application, self.persistence, object(), verification_id="verify1")


if __name__ == "__main__":
    unittest.main()
