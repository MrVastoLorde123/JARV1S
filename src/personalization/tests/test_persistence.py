import json
import tempfile
import unittest
from pathlib import Path

from src.personalization.persistence import (
    PersonalizationPersistenceConflictError,
    PersonalizationRecord,
    PersonalizationState,
    PersonalizationStore,
)
from src.personalization.profile import PersonalizationSignal, build_profile


class PersonalizationPersistenceTests(unittest.TestCase):
    def signal(self, *, signal_id="pref-1", value="concise"):
        return PersonalizationSignal(
            signal_id=signal_id,
            category="PREFERENCE",
            key="response_style",
            value=value,
            confidence=0.9,
            importance=0.8,
            source_ids=("memory:1", "evidence:1"),
            explicit_user_preference=True,
        )

    def profile(self, signal=None):
        return build_profile(
            "profile-1",
            (signal or self.signal(),),
            provenance={"source": "test"},
        )

    def test_persists_and_restores_active_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "personalization.json"
            store = PersonalizationStore(path)
            persisted = store.persist_profile(self.profile())
            self.assertEqual(len(persisted), 1)
            self.assertTrue(path.exists())

            restored = PersonalizationStore(path)
            profile = restored.active_profile("restored")
            self.assertEqual(len(profile.preferences), 1)
            self.assertEqual(profile.preferences[0].value, "concise")

    def test_persistence_is_idempotent_for_same_signal(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            first = store.persist_profile(self.profile())
            second = store.persist_profile(self.profile())
            self.assertEqual(first, second)
            self.assertEqual(len(store.records()), 1)

    def test_conflicting_signal_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            store.persist_profile(self.profile())
            conflicting = self.profile(self.signal(value="verbose"))
            with self.assertRaises(PersonalizationPersistenceConflictError):
                store.persist_profile(conflicting)

    def test_reversal_removes_signal_from_active_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            store.persist_profile(self.profile())
            reversed_record = store.reverse(
                "personalization:pref-1",
                "user-reversal-1",
            )
            self.assertEqual(reversed_record.state, PersonalizationState.REVERSED)
            self.assertEqual(reversed_record.reversal_reference, "user-reversal-1")
            self.assertEqual(store.active_profile().signals, ())

            restored = PersonalizationStore(Path(directory) / "personalization.json")
            record = restored.get("personalization:pref-1")
            self.assertIsNotNone(record)
            self.assertEqual(record.state, PersonalizationState.REVERSED)
            self.assertEqual(restored.active_profile().signals, ())

    def test_only_active_records_are_projected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            store.persist_profile(
                build_profile(
                    "profile-1",
                    (self.signal(signal_id="a"), self.signal(signal_id="b", value="detailed")),
                    provenance={"source": "test"},
                )
            )
            store.reverse("personalization:a", "undo-a")
            profile = store.active_profile()
            self.assertEqual([signal.signal_id for signal in profile.signals], ["b"])

    def test_reversal_requires_active_record_and_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            with self.assertRaises(KeyError):
                store.reverse("missing", "undo")
            store.persist_profile(self.profile())
            with self.assertRaises(ValueError):
                store.reverse("personalization:pref-1", "")
            store.reverse("personalization:pref-1", "undo")
            with self.assertRaises(ValueError):
                store.reverse("personalization:pref-1", "undo-again")

    def test_serialized_state_is_non_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "personalization.json"
            PersonalizationStore(path).persist_profile(self.profile())
            data = json.loads(path.read_text(encoding="utf-8"))
            record = data["records"][0]
            self.assertFalse(record["authority_granted"])
            self.assertFalse(record["authorization_granted"])
            self.assertFalse(record["policy_mutation"])
            self.assertFalse(record["execution_requested"])

    def test_record_round_trip_is_stable(self):
        record = PersonalizationRecord(record_id="r1", signal=self.signal())
        restored = PersonalizationRecord.from_dict(record.to_dict())
        self.assertEqual(restored.record_id, record.record_id)
        self.assertEqual(restored.signal, record.signal)
        self.assertEqual(restored.state, PersonalizationState.ACTIVE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
