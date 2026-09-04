import json
import tempfile
import unittest
from pathlib import Path

from src.interface.session_identity import PersistentSessionIdentity


class PersistentSessionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_directory.name) / "session.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_creates_and_persists_session_identity(self):
        store = PersistentSessionIdentity(self.path)
        first = store.get_or_create()

        self.assertTrue(first.startswith("local-"))
        self.assertEqual(store.get_or_create(), first)
        self.assertEqual(
            json.loads(self.path.read_text(encoding="utf-8"))["session_id"],
            first,
        )

    def test_restart_reads_existing_identity(self):
        first_store = PersistentSessionIdentity(self.path)
        first = first_store.get_or_create()

        second_store = PersistentSessionIdentity(self.path)
        self.assertEqual(second_store.get_or_create(), first)

    def test_new_session_replaces_persisted_identity(self):
        store = PersistentSessionIdentity(self.path)
        first = store.get_or_create()
        second = store.new_session()

        self.assertNotEqual(first, second)
        self.assertEqual(store.get_or_create(), second)

    def test_requested_session_id_is_persisted(self):
        store = PersistentSessionIdentity(self.path)
        self.assertEqual(store.get_or_create("session-explicit"), "session-explicit")
        self.assertEqual(store.get_or_create(), "session-explicit")

    def test_invalid_stored_identity_is_replaced(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"session_id": "   "}),
            encoding="utf-8",
        )

        store = PersistentSessionIdentity(self.path)
        session_id = store.get_or_create()

        self.assertTrue(session_id.startswith("local-"))
        self.assertNotEqual(session_id, "   ")

    def test_malformed_file_is_recovered(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("not-json", encoding="utf-8")

        store = PersistentSessionIdentity(self.path)
        session_id = store.get_or_create()

        self.assertTrue(session_id.startswith("local-"))
        self.assertEqual(store.get_or_create(), session_id)

    def test_empty_requested_identity_is_rejected(self):
        store = PersistentSessionIdentity(self.path)
        with self.assertRaises(ValueError):
            store.get_or_create("   ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
