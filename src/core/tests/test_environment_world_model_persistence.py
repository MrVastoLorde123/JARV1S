import tempfile
import unittest
from pathlib import Path

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_persistence import (
    EnvironmentWorldModelPersistenceError,
    FileEnvironmentWorldModelStore,
)


class EnvironmentWorldModelPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.store = FileEnvironmentWorldModelStore(self.root)
        self.model = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86", "ram_gb": 16}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
            lineage={"source": {"stage": "world-model"}},
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_empty_store_returns_none(self) -> None:
        self.assertIsNone(self.store.get("env-1"))

    def test_put_and_get_round_trip_preserves_identity_and_data(self) -> None:
        self.store.put(self.model)
        loaded = self.store.get("env-1")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.model_id, "model-1")
        self.assertEqual(dict(loaded.state_by_domain["hardware"]), {"cpu": "x86", "ram_gb": 16})
        self.assertEqual(loaded.represented_domains, ("hardware",))
        self.assertEqual(loaded.missing_domains, ("software", "network"))
        self.assertEqual(loaded.lineage["source"]["stage"], "world-model")

    def test_persistence_reconstructs_immutable_model(self) -> None:
        self.store.put(self.model)
        loaded = self.store.get("env-1")
        with self.assertRaises(TypeError):
            loaded.state_by_domain["hardware"]["cpu"] = "arm"

    def test_expected_model_id_enforces_compare_and_swap(self) -> None:
        self.store.put(self.model)
        replacement = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.store.put(replacement, expected_model_id="model-1")
        self.assertEqual(self.store.get("env-1").model_id, "model-2")

    def test_wrong_expected_model_id_fails_without_change(self) -> None:
        self.store.put(self.model)
        replacement = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        with self.assertRaises(EnvironmentWorldModelPersistenceError):
            self.store.put(replacement, expected_model_id="wrong")
        self.assertEqual(self.store.get("env-1").model_id, "model-1")

    def test_absent_expected_model_fails_without_creation(self) -> None:
        with self.assertRaises(EnvironmentWorldModelPersistenceError):
            self.store.put(self.model, expected_model_id="model-1")
        self.assertIsNone(self.store.get("env-1"))

    def test_remove_returns_model_and_clears_store(self) -> None:
        self.store.put(self.model)
        removed = self.store.remove("env-1")
        self.assertEqual(removed.model_id, "model-1")
        self.assertIsNone(self.store.get("env-1"))

    def test_remove_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.remove("env-1"))

    def test_invalid_environment_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.get("")
        with self.assertRaises(ValueError):
            self.store.get("../escape")
        with self.assertRaises(ValueError):
            self.store.get("nested/env")

    def test_wrong_model_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.store.put(object())

    def test_corrupt_payload_fails_closed(self) -> None:
        path = self.root / "env-1.json"
        path.write_text("{not-json", encoding="utf-8")
        with self.assertRaises(EnvironmentWorldModelPersistenceError):
            self.store.get("env-1")

    def test_invalid_persisted_environment_identity_fails_closed(self) -> None:
        self.store.put(self.model)
        path = self.root / "env-1.json"
        text = path.read_text(encoding="utf-8").replace('"environment_id": "env-1"', '"environment_id": "env-2"')
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(EnvironmentWorldModelPersistenceError):
            self.store.get("env-1")

    def test_persistence_is_environment_scoped(self) -> None:
        second = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-2",
            state_by_domain={"network": {"status": "up"}},
            represented_domains=("network",),
            missing_domains=("hardware", "software"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.store.put(self.model)
        self.store.put(second)
        self.assertEqual(self.store.get("env-1").model_id, "model-1")
        self.assertEqual(self.store.get("env-2").model_id, "model-2")

    def test_source_model_is_not_mutated(self) -> None:
        before = dict(self.model.state_by_domain["hardware"])
        self.store.put(self.model)
        self.assertEqual(dict(self.model.state_by_domain["hardware"]), before)


if __name__ == "__main__":
    unittest.main()
