import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.core.tool_execution_verification import ToolExecutionVerification, ToolVerificationStatus
from src.core.tool_execution_verification_evidence_store import (
    ToolExecutionVerificationEvidenceStore,
)
from src.tools.models import ToolRequest, ToolResult


class ToolExecutionVerificationEvidenceStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp.name) / "verification.db"
        self.store = ToolExecutionVerificationEvidenceStore(self.database_path)
        self.request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="inv-1",
        )
        self.result = ToolResult(
            success=True,
            tool_name="ping_host",
            content={"reachable": True, "latency_ms": 1},
            metadata={"source": "icmp"},
            invocation_id="inv-1",
        )
        self.verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.VERIFIED,
            evidence="independent reachability check",
            reason="observed host response matched expected effect",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_save_and_round_trip(self):
        stored = self.store.save(self.verification)
        loaded = self.store.get(stored.evidence_id)
        self.assertEqual(stored, loaded)

    def test_identical_verification_is_idempotent(self):
        first = self.store.save(self.verification)
        second = self.store.save(self.verification)
        self.assertEqual(first, second)
        self.assertEqual(1, len(self.store.all()))

    def test_different_status_changes_identity(self):
        first = self.store.save(self.verification)
        second = self.store.save(
            ToolExecutionVerification(
                request=self.request,
                result=self.result,
                status=ToolVerificationStatus.UNVERIFIED,
                evidence="insufficient evidence",
                reason="independent effect could not be confirmed",
            )
        )
        self.assertNotEqual(first.evidence_id, second.evidence_id)
        self.assertEqual(2, len(self.store.all()))

    def test_invocation_query_is_scoped(self):
        self.store.save(self.verification)
        other = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.2"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="inv-2",
        )
        self.store.save(ToolExecutionVerification(
            request=other,
            result=ToolResult(
                success=True,
                tool_name="ping_host",
                content={"reachable": False},
                invocation_id="inv-2",
            ),
            status=ToolVerificationStatus.FAILED,
            evidence="host refused response",
            reason="expected effect was not observed",
        ))
        records = self.store.list_for_invocation("inv-1")
        self.assertEqual(1, len(records))
        self.assertEqual("inv-1", records[0].verification.request.invocation_id)

    def test_empty_lookup_is_rejected(self):
        with self.assertRaises(ValueError):
            self.store.get("")
        with self.assertRaises(ValueError):
            self.store.list_for_invocation("")

    def test_non_verification_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.store.save(object())  # type: ignore[arg-type]

    def test_persistence_is_json_native(self):
        stored = self.store.save(self.verification)
        record = json.loads(stored.verification_store_record if hasattr(stored, "verification_store_record") else "{}")
        self.assertIsInstance(record, dict)

    def test_tampered_row_is_rejected(self):
        stored = self.store.save(self.verification)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE tool_execution_verification_evidence SET reason = ? WHERE evidence_id = ?",
                ("tampered", stored.evidence_id),
            )
        with self.assertRaises(ValueError):
            self.store.get(stored.evidence_id)

    def test_all_rejects_tampered_row(self):
        stored = self.store.save(self.verification)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE tool_execution_verification_evidence SET evidence = ? WHERE evidence_id = ?",
                ("tampered", stored.evidence_id),
            )
        with self.assertRaises(ValueError):
            self.store.all()

    def test_invocation_query_rejects_tampered_row(self):
        stored = self.store.save(self.verification)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE tool_execution_verification_evidence SET status = ? WHERE evidence_id = ?",
                ("FAILED", stored.evidence_id),
            )
        with self.assertRaises(ValueError):
            self.store.list_for_invocation("inv-1")


if __name__ == "__main__":
    unittest.main()
