import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MEMORY_DIRECTORY = Path(__file__).resolve().parent.parent

if str(MEMORY_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(MEMORY_DIRECTORY))

import evidence_store
from src import database

class EvidenceStoreTests(unittest.TestCase):

    def setUp(self):

        self.temp_directory = tempfile.TemporaryDirectory()

        self.database_path = (
            Path(self.temp_directory.name) / "test_jarvis.db"
        )

        database.set_database_path(self.database_path)

        connection = sqlite3.connect(self.database_path)

        connection.execute("PRAGMA foreign_keys = ON")

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY
            )
        """)

        cursor.execute("""
            CREATE TABLE memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                source_conversation_id TEXT,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                memory_key TEXT,
                importance REAL NOT NULL DEFAULT 0.5,
                status TEXT NOT NULL DEFAULT 'ACTIVE'
            )
        """)

        cursor.execute("""
            CREATE TABLE memory_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                memory_id INTEGER NOT NULL,

                conversation_id TEXT,
                message_id TEXT,

                evidence_text TEXT NOT NULL,

                evidence_type TEXT NOT NULL,

                confidence REAL NOT NULL,

                source_created_at TEXT,

                created_at TEXT NOT NULL,

                FOREIGN KEY (memory_id)
                    REFERENCES memories(id),

                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
            )
        """)

        cursor.execute("""
            INSERT INTO memories (
                content,
                category,
                confidence,
                created_at,
                updated_at,
                memory_key,
                importance,
                status
            )
            VALUES (
                'User is actively learning PCVUE v17.',
                'SKILL',
                0.95,
                '2026-08-15T12:00:00',
                '2026-08-15T12:00:00',
                'pcvue_skill',
                0.90,
                'ACTIVE'
            )
        """)

        cursor.execute("""
            INSERT INTO conversations (id)
            VALUES ('conversation-001')
        """)

        connection.commit()
        connection.close()

    def tearDown(self):

        self.temp_directory.cleanup()

    def test_valid_evidence_is_created(self):

        evidence_id = evidence_store.add_evidence(
            memory_id=1,
            evidence_text="User explicitly says they are learning PCVUE.",
            evidence_type="DIRECT",
            confidence=0.98
        )

        self.assertEqual(evidence_id, 1)

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(len(evidence), 1)

    def test_invalid_evidence_type_is_rejected(self):

        evidence_id = evidence_store.add_evidence(
            memory_id=1,
            evidence_text="Some evidence.",
            evidence_type="NONSENSE",
            confidence=0.90
        )

        self.assertIsNone(evidence_id)

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(len(evidence), 0)

    def test_invalid_confidence_is_rejected(self):

        evidence_id = evidence_store.add_evidence(
            memory_id=1,
            evidence_text="Some evidence.",
            evidence_type="DIRECT",
            confidence=1.5
        )

        self.assertIsNone(evidence_id)

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(len(evidence), 0)

    def test_missing_evidence_text_is_rejected(self):

        evidence_id = evidence_store.add_evidence(
            memory_id=1,
            evidence_text="",
            evidence_type="DIRECT",
            confidence=0.90
        )

        self.assertIsNone(evidence_id)

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(len(evidence), 0)

    def test_nonexistent_memory_is_rejected(self):

        evidence_id = evidence_store.add_evidence(
            memory_id=999,
            evidence_text="This memory does not exist.",
            evidence_type="DIRECT",
            confidence=0.90
        )

        self.assertIsNone(evidence_id)

    def test_evidence_is_normalized(self):

        evidence_store.add_evidence(
            memory_id=1,
            evidence_text="User says they are learning PCVUE.",
            evidence_type="direct",
            confidence=0.95
        )

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(evidence[0][5], "DIRECT")

    def test_source_references_are_stored(self):

        evidence_store.add_evidence(
            memory_id=1,
            evidence_text="User explicitly mentions PCVUE v17.",
            evidence_type="DIRECT",
            confidence=0.99,
            conversation_id="conversation-001",
            message_id="message-123",
            source_created_at="2026-08-15T10:00:00"
        )

        evidence = evidence_store.get_evidence_for_memory(1)

        self.assertEqual(
            evidence[0][2],
            "conversation-001"
        )

        self.assertEqual(
            evidence[0][3],
            "message-123"
        )

        self.assertEqual(
            evidence[0][7],
            "2026-08-15T10:00:00"
        )

    def test_evidence_can_be_retrieved_by_conversation(self):

        evidence_store.add_evidence(
            memory_id=1,
            evidence_text="User explicitly mentions PCVUE.",
            evidence_type="DIRECT",
            confidence=0.95,
            conversation_id="conversation-001"
        )

        evidence = (
            evidence_store
            .get_evidence_for_conversation(
                "conversation-001"
            )
        )

        self.assertEqual(len(evidence), 1)

        self.assertEqual(evidence[0][1], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)