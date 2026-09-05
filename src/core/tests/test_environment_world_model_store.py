import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_store import (
    EnvironmentWorldModelStoreError,
    InMemoryEnvironmentWorldModelStore,
)


class EnvironmentWorldModelStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model1 = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.model2 = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.store = InMemoryEnvironmentWorldModelStore()

    def test_empty_store_returns_none(self) -> None:
        self.assertIsNone(self.store.get("env-1"))

    def test_put_and_get_preserve_model_identity(self) -> None:
        stored = self.store.put(self.model1)
        self.assertIs(stored, self.model1)
        self.assertIs(self.store.get("env-1"), self.model1)

    def test_put_replaces_current_model(self) -> None:
        self.store.put(self.model1)
        self.store.put(self.model2)
        self.assertIs(self.store.get("env-1"), self.model2)

    def test_expected_model_id_enforces_compare_and_swap(self) -> None:
        self.store.put(self.model1)
        self.store.put(self.model2, expected_model_id="model-1")
        self.assertIs(self.store.get("env-1"), self.model2)

    def test_wrong_expected_model_id_fails_closed(self) -> None:
        self.store.put(self.model1)
        with self.assertRaises(EnvironmentWorldModelStoreError):
            self.store.put(self.model2, expected_model_id="wrong")
        self.assertIs(self.store.get("env-1"), self.model1)

    def test_expected_model_requires_existing_current_state(self) -> None:
        with self.assertRaises(EnvironmentWorldModelStoreError):
            self.store.put(self.model1, expected_model_id="model-0")

    def test_invalid_expected_model_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.put(self.model1, expected_model_id="")

    def test_wrong_model_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.store.put(object())

    def test_invalid_environment_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.get("")
        with self.assertRaises(ValueError):
            self.store.remove("")

    def test_remove_returns_and_clears_current_model(self) -> None:
        self.store.put(self.model1)
        removed = self.store.remove("env-1")
        self.assertIs(removed, self.model1)
        self.assertIsNone(self.store.get("env-1"))

    def test_remove_missing_environment_returns_none(self) -> None:
        self.assertIsNone(self.store.remove("env-1"))

    def test_store_does_not_mutate_models(self) -> None:
        before = dict(self.model1.state_by_domain["hardware"])
        self.store.put(self.model1)
        self.store.remove("env-1")
        self.assertEqual(dict(self.model1.state_by_domain["hardware"]), before)

    def test_store_is_environment_scoped(self) -> None:
        model_other = EnvironmentWorldModel(
            model_id="model-other",
            environment_id="env-2",
            state_by_domain={"hardware": {"cpu": "riscv"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-other",),
            qualification_ids=("qual-other",),
            provenance_ids=("prov-other",),
            readiness_id="ready-other",
            source_bundle_id="bundle-other",
        )
        self.store.put(self.model1)
        self.store.put(model_other)
        self.assertIs(self.store.get("env-1"), self.model1)
        self.assertIs(self.store.get("env-2"), model_other)


if __name__ == "__main__":
    unittest.main()
