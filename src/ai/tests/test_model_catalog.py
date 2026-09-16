import unittest

from src.ai.model_catalog import ModelCatalog, ModelObservation
from src.ai.model_routing import ModelProfile, ModelRole


class ModelCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = ModelCatalog(
            [
                ModelProfile(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}),
                    priority=100,
                ),
                ModelProfile(
                    "qwen3-14b",
                    frozenset({ModelRole.DIAGNOSTIC}),
                    priority=90,
                ),
            ]
        )

    def test_unobserved_profile_is_not_reported_available_after_sync(self) -> None:
        self.catalog.observe_ids(["granite-8b"])
        self.assertTrue(self.catalog.profile("granite-8b").available)
        self.assertFalse(self.catalog.profile("qwen3-14b").available)

    def test_observation_can_mark_known_model_available(self) -> None:
        self.catalog.observe(ModelObservation("qwen3-14b", observed=True))
        self.assertTrue(self.catalog.profile("qwen3-14b").available)

    def test_openai_models_payload_is_observed_without_inventing_profiles(self) -> None:
        observed = self.catalog.observe_openai_models(
            {"data": [{"id": "granite-8b"}, {"id": "unknown-model"}]}
        )
        self.assertEqual(observed, ("granite-8b", "unknown-model"))
        self.assertEqual(self.catalog.observed_model_ids(), ("granite-8b", "unknown-model"))
        self.assertFalse(self.catalog.profile("qwen3-14b").available)
        with self.assertRaisesRegex(KeyError, "unknown model"):
            self.catalog.profile("unknown-model")

    def test_unknown_observations_follow_latest_provider_snapshot(self) -> None:
        self.catalog.observe_openai_models(
            {"data": [{"id": "granite-8b"}, {"id": "old-unknown-model"}]}
        )
        self.catalog.observe_openai_models(
            {"data": [{"id": "granite-8b"}, {"id": "new-unknown-model"}]}
        )
        self.assertEqual(
            self.catalog.observed_model_ids(),
            ("granite-8b", "new-unknown-model"),
        )

    def test_observation_does_not_grant_authority(self) -> None:
        self.catalog.observe(ModelObservation("granite-8b", observed=True))
        profile = self.catalog.profile("granite-8b")
        self.assertFalse(hasattr(profile, "authority"))
        self.assertFalse(hasattr(profile, "permissions"))
        self.assertFalse(hasattr(profile, "tools"))

    def test_invalid_models_payload_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "data.*sequence"):
            self.catalog.observe_openai_models({"data": {"id": "granite-8b"}})

    def test_non_mapping_models_payload_is_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "payload must be a mapping"):
            self.catalog.observe_openai_models([])

    def test_observation_requires_nonempty_model_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "model_id cannot be empty"):
            ModelObservation("   ")

    def test_roles_for_requires_model_role_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "roles must contain only ModelRole"):
            ModelCatalog.roles_for("GENERAL")

    def test_identical_profile_registration_is_idempotent(self) -> None:
        profile = ModelProfile("granite-8b", frozenset({ModelRole.GENERAL}), priority=100)
        catalog = ModelCatalog([profile])
        catalog.register_profile(profile)
        self.assertEqual(catalog.profile("granite-8b"), profile)

    def test_conflicting_profile_registration_is_rejected(self) -> None:
        profile = ModelProfile("granite-8b", frozenset({ModelRole.GENERAL}), priority=100)
        with self.assertRaisesRegex(ValueError, "conflicting profile"):
            self.catalog.register_profile(profile)


if __name__ == "__main__":
    unittest.main()
