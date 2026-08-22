import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database
from src.memory import memory_retrieval


class MemoryRetrievalTests(unittest.TestCase):

    def setUp(self):

        self.original_database_path = database.DATABASE_PATH

        self.temp_directory = tempfile.TemporaryDirectory()

        self.database_path = (
            Path(self.temp_directory.name)
            / "test_jarvis.db"
        )

        database.set_database_path(
            self.database_path
        )

        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = connection.cursor()

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
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY
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
                'User is building JARVIS PREMATURE.',
                'PROJECT',
                0.98,
                '2026-08-15T12:00:00',
                '2026-08-15T12:00:00',
                'jarvis_project',
                1.00,
                'ACTIVE'
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
                'User previously experimented with Java.',
                'SKILL',
                0.80,
                '2026-08-15T12:00:00',
                '2026-08-15T12:00:00',
                'java_skill',
                0.40,
                'SUPERSEDED'
            )
        """)

        cursor.execute("""
            INSERT INTO conversations (id)
            VALUES ('conversation-001')
        """)

        cursor.execute("""
            INSERT INTO memory_evidence (
                memory_id,
                conversation_id,
                message_id,
                evidence_text,
                evidence_type,
                confidence,
                source_created_at,
                created_at
            )
            VALUES (
                1,
                'conversation-001',
                'message-001',
                'User explicitly says they are learning PCVUE.',
                'DIRECT',
                0.98,
                '2026-08-15T10:00:00',
                '2026-08-15T12:00:00'
            )
        """)

        connection.commit()
        connection.close()

    def tearDown(self):

        database.set_database_path(
            self.original_database_path
        )

        self.temp_directory.cleanup()

    def test_exact_memory_can_be_retrieved(self):

        result = memory_retrieval.get_memory(
            "pcvue_skill"
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.memory_key,
            "pcvue_skill"
        )

        self.assertEqual(
            result.category,
            "SKILL"
        )

    def test_nonexistent_memory_returns_none(self):

        result = memory_retrieval.get_memory(
            "does_not_exist"
        )

        self.assertIsNone(result)

    def test_category_retrieval_returns_active_memories(self):

        results = (
            memory_retrieval
            .get_memories_by_category("SKILL")
        )

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0].memory_key,
            "pcvue_skill"
        )

    def test_category_retrieval_is_case_insensitive(self):

        results = (
            memory_retrieval
            .get_memories_by_category("skill")
        )

        self.assertEqual(len(results), 1)

    def test_inactive_memories_are_not_returned(self):

        result = memory_retrieval.get_memory(
            "java_skill"
        )

        self.assertIsNone(result)

    def test_search_finds_matching_memory(self):

        results = memory_retrieval.search_memories(
            "PCVUE"
        )

        self.assertGreaterEqual(
            len(results),
            1
        )

        self.assertEqual(
            results[0].memory_key,
            "pcvue_skill"
        )

    def test_search_is_case_insensitive(self):

        results = memory_retrieval.search_memories(
            "pcvue"
        )

        self.assertGreaterEqual(
            len(results),
            1
        )

        self.assertEqual(
            results[0].memory_key,
            "pcvue_skill"
        )

    def test_unrelated_search_returns_empty_list(self):

        results = memory_retrieval.search_memories(
            "astronautics"
        )

        self.assertEqual(
            results,
            []
        )

    def test_search_returns_relevance_score(self):

        results = memory_retrieval.search_memories(
            "PCVUE"
        )

        self.assertEqual(
            results[0].relevance_score,
            1.0
        )

    def test_memory_with_evidence_returns_evidence(self):

        result = (
            memory_retrieval
            .get_memory_with_evidence(1)
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            len(result.evidence),
            1
        )

        self.assertEqual(
            result.evidence[0][4],
            "User explicitly says they are learning PCVUE."
        )

    def test_retrieval_does_not_modify_memory(self):

        before = memory_retrieval.get_memory(
            "pcvue_skill"
        )

        memory_retrieval.search_memories(
            "PCVUE"
        )

        after = memory_retrieval.get_memory(
            "pcvue_skill"
        )

        self.assertEqual(
            before.content,
            after.content
        )

        self.assertEqual(
            before.confidence,
            after.confidence
        )

        self.assertEqual(
            before.importance,
            after.importance
        )

        self.assertEqual(
            before.status,
            after.status
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)