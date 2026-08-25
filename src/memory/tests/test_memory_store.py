import sqlite3
import tempfile
import unittest
from pathlib import Path


from src.memory import memory_store
from src import database


class MemoryStoreTests(unittest.TestCase):

    def setUp(self):
        """
        Create a completely separate temporary database
        for every test.
        """

        self.temp_directory = tempfile.TemporaryDirectory()

        self.database_path = (
            Path(self.temp_directory.name) / "test_jarvis.db"
        )

        database.set_database_path(self.database_path)

        connection = sqlite3.connect(self.database_path)
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
                status TEXT NOT NULL DEFAULT 'ACTIVE',

                FOREIGN KEY (source_conversation_id)
                    REFERENCES conversations(id)
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX
            idx_unique_active_memory_key
            ON memories(memory_key)
            WHERE status = 'ACTIVE'
              AND memory_key IS NOT NULL
        """)

        connection.commit()
        connection.close()

    def tearDown(self):
        """
        Remove the temporary database after each test.
        """

        self.temp_directory.cleanup()

    def test_valid_memory_is_created(self):

        memory_id = memory_store.add_memory(
            content="User is actively learning PCVUE v17.",
            category="SKILL",
            memory_key="pcvue_skill",
            confidence=0.95,
            importance=0.90,
            status="ACTIVE"
        )

        self.assertEqual(memory_id, 1)

        memories = memory_store.list_memories()

        self.assertEqual(len(memories), 1)

    def test_duplicate_memory_is_not_created(self):

        first_id = memory_store.add_memory(
            content="User is actively learning PCVUE v17.",
            category="SKILL",
            memory_key="pcvue_skill",
            confidence=0.95,
            importance=0.90,
            status="ACTIVE"
        )

        second_id = memory_store.add_memory(
            content="User is actively learning PCVUE v17.",
            category="SKILL",
            memory_key="pcvue_skill",
            confidence=0.95,
            importance=0.90,
            status="ACTIVE"
        )

        self.assertEqual(first_id, 1)
        self.assertEqual(second_id, 1)

        memories = memory_store.list_memories()

        self.assertEqual(len(memories), 1)

    def test_invalid_memory_is_rejected(self):

        memory_id = memory_store.add_memory(
            content="",
            category="INVALID_CATEGORY",
            memory_key="invalid_test",
            confidence=2.0,
            importance=-1.0,
            status="UNKNOWN"
        )

        self.assertIsNone(memory_id)

        memories = memory_store.list_memories()

        self.assertEqual(len(memories), 0)

    def test_category_is_normalized(self):

        memory_store.add_memory(
            content="User is actively learning PCVUE v17.",
            category="skill",
            memory_key="pcvue_skill",
            confidence=0.95,
            importance=0.90,
            status="active"
        )

        memories = memory_store.list_memories()

        self.assertEqual(memories[0][3], "SKILL")
        self.assertEqual(memories[0][6], "ACTIVE")

    def test_different_memory_keys_are_allowed(self):

        first_id = memory_store.add_memory(
            content="User is actively learning PCVUE v17.",
            category="SKILL",
            memory_key="pcvue_skill",
            confidence=0.95,
            importance=0.90
        )

        second_id = memory_store.add_memory(
            content="User is building a personal AI assistant.",
            category="PROJECT",
            memory_key="jarvis_project",
            confidence=0.95,
            importance=1.0
        )

        self.assertEqual(first_id, 1)
        self.assertEqual(second_id, 2)

        memories = memory_store.list_memories()

        self.assertEqual(len(memories), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)