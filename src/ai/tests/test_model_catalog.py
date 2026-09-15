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

    def test_observation_does_not_grant_authority(self) -> None:
        self.catalog.observe(ModelObservation("granite-8b", observed=True))
        profile = self.catalog.profile("granite-8b")
        self.assertFalse(hasattr(profile, "authority"))
        self.assertFalse(hasattr(profile, "permissions"))
        self.assertFalse(hasattr(profile, "tools"))

    def test_invalid_models_payload_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "data.*sequence"):
            self.catalog.observe_openai_models({"data": {"id": "granite-8b"}})


if __name__ == "__main__":
    unittest.main()
