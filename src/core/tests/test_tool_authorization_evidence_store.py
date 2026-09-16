import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.core.tool_authorization_evidence_store import (
    ToolAuthorizationEvidenceStore,
)


class ToolAuthorizationEvidenceStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "authorization.db"
        self.store = ToolAuthorizationEvidenceStore(self.database_path)
        self.evidence = ToolAuthorizationEvidence(
            step_id="step-1",
            invocation_id="inv-1",
            tool_name="ping_host",
            scope="diagnostics",
            capability_class="diagnostic",
            authorized=True,
            policy_id="ops-read",
            reason="request matches policy allow rules",
        )

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_save_returns_stable_id_and_round_trips(self) -> None:
        stored = self.store.save(self.evidence)
        loaded = self.store.get(stored.evidence_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded, stored)

    def test_identical_evidence_is_idempotent(self) -> None:
        first = self.store.save(self.evidence)
        second = self.store.save(self.evidence)
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.all()), 1)

    def test_different_evidence_gets_different_identity(self) -> None:
        first = self.store.save(self.evidence)
        second = self.store.save(
            ToolAuthorizationEvidence(
                step_id="step-1",
                invocation_id="inv-2",
                tool_name="ping_host",
                scope="diagnostics",
                capability_class="diagnostic",
                authorized=False,
                policy_id="ops-read",
                reason="tool 'ping_host' is denied",
            )
        )
        self.assertNotEqual(first.evidence_id, second.evidence_id)
        self.assertEqual(len(self.store.all()), 2)

    def test_get_missing_evidence_returns_none(self) -> None:
        self.assertIsNone(self.store.get("missing"))

    def test_step_query_is_scoped_and_deterministic(self) -> None:
        self.store.save(self.evidence)
        self.store.save(
            ToolAuthorizationEvidence(
                step_id="step-2",
                invocation_id="inv-2",
                tool_name="read_status",
                scope="diagnostics",
                capability_class="diagnostic",
                authorized=True,
                policy_id="ops-read",
                reason="request matches policy allow rules",
            )
        )
        results = self.store.list_for_step("step-1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].evidence, self.evidence)

    def test_persistence_is_independent_from_execution_result_shape(self) -> None:
        stored = self.store.save(self.evidence)
        serialized = json.dumps(stored.evidence.to_record(), sort_keys=True)
        self.assertIn('"authorized": true', serialized)
        self.assertNotIn("success", serialized)
        self.assertNotIn("content", serialized)

    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.store.save(object())  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.store.get("")
        with self.assertRaises(ValueError):
            self.store.list_for_step("")

    def test_get_rejects_tampered_row(self) -> None:
        stored = self.store.save(self.evidence)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE tool_authorization_evidence SET reason = ? WHERE evidence_id = ?",
                ("tampered", stored.evidence_id),
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaisesRegex(ValueError, "integrity validation"):
            self.store.get(stored.evidence_id)

    def test_all_rejects_tampered_row(self) -> None:
        stored = self.store.save(self.evidence)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE tool_authorization_evidence SET authorized = ? WHERE evidence_id = ?",
                (0, stored.evidence_id),
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaisesRegex(ValueError, "integrity validation"):
            self.store.all()

    def test_step_query_rejects_tampered_row(self) -> None:
        stored = self.store.save(self.evidence)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE tool_authorization_evidence SET tool_name = ? WHERE evidence_id = ?",
                ("other_tool", stored.evidence_id),
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaisesRegex(ValueError, "integrity validation"):
            self.store.list_for_step("step-1")


if __name__ == "__main__":
    unittest.main()
