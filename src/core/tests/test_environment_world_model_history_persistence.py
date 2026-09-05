import tempfile
import unittest
from pathlib import Path

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import EnvironmentWorldModelHistory
from src.core.environment_world_model_history_persistence import (
    EnvironmentWorldModelHistoryPersistenceError,
    FileEnvironmentWorldModelHistoryStore,
)


class EnvironmentWorldModelHistoryPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.store = FileEnvironmentWorldModelHistoryStore(self.root)
        self.model_1 = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
            lineage={"source": {"stage": "observation"}},
        )
        self.model_2 = EnvironmentWorldModel(
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
            lineage={"source": {"stage": "revision"}},
        )
        self.history = EnvironmentWorldModelHistory(
            environment_id="env-1",
            models=(self.model_1, self.model_2),
            lineage={"reason": "accepted revision"},
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_empty_store_returns_none(self) -> None:
        self.assertIsNone(self.store.get("env-1"))

    def test_round_trip_preserves_order_and_latest(self) -> None:
        self.store.put(self.history)
        loaded = self.store.get("env-1")
        self.assertEqual(loaded.environment_id, "env-1")
        self.assertEqual(loaded.model_ids, ("model-1", "model-2"))
        self.assertEqual(loaded.latest.model_id, "model-2")
        self.assertEqual(loaded.models[1].state_by_domain["hardware"]["cpu"], "arm64")

    def test_round_trip_preserves_nested_immutability(self) -> None:
        self.store.put(self.history)
        loaded = self.store.get("env-1")
        with self.assertRaises(TypeError):
            loaded.lineage["reason"] = "changed"
        with self.assertRaises(TypeError):
            loaded.models[0].state_by_domain["hardware"]["cpu"] = "mutated"

    def test_history_environment_identity_is_enforced(self) -> None:
        path = self.root / "env-1.json"
        self.store.put(self.history)
        text = path.read_text(encoding="utf-8").replace('"environment_id": "env-1"', '"environment_id": "env-2"', 1)
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(EnvironmentWorldModelHistoryPersistenceError):
            self.store.get("env-1")

    def test_corrupt_payload_fails_closed(self) -> None:
        path = self.root / "env-1.json"
        path.write_text("{not-json", encoding="utf-8")
        with self.assertRaises(EnvironmentWorldModelHistoryPersistenceError):
            self.store.get("env-1")

    def test_invalid_persisted_model_fails_closed(self) -> None:
        self.store.put(self.history)
        path = self.root / "env-1.json"
        text = path.read_text(encoding="utf-8").replace('"model_id": "model-2"', '"model_id": "model-1"', 1)
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(EnvironmentWorldModelHistoryPersistenceError):
            self.store.get("env-1")

    def test_path_safe_environment_ids_only(self) -> None:
        with self.assertRaises(ValueError):
            self.store.get("../escape")
        with self.assertRaises(ValueError):
            self.store.get("nested/env")

    def test_wrong_history_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.store.put(object())

    def test_remove_returns_history_and_clears_store(self) -> None:
        self.store.put(self.history)
        removed = self.store.remove("env-1")
        self.assertEqual(removed.model_ids, ("model-1", "model-2"))
        self.assertIsNone(self.store.get("env-1"))

    def test_remove_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.remove("env-1"))

    def test_source_history_is_not_mutated(self) -> None:
        before = self.history.model_ids
        self.store.put(self.history)
        self.assertEqual(self.history.model_ids, before)


if __name__ == "__main__":
    unittest.main()
