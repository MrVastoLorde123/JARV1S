import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.commands.handlers.memory import (
    ShowMemoryHandler,
)

from src.commands.models import (
    CommandRequest,
)


def create_test_schema(
    database_path,
):
    connection = sqlite3.connect(
        database_path
    )

    try:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY
            )
            """
        )

        cursor.execute(
            """
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

                FOREIGN KEY (
                    source_conversation_id
                )
                REFERENCES conversations(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX
            idx_unique_active_memory_key
            ON memories(memory_key)
            WHERE status = 'ACTIVE'
              AND memory_key IS NOT NULL
            """
        )

        cursor.execute(
            """
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

                FOREIGN KEY (
                    memory_id
                )
                REFERENCES memories(id),

                FOREIGN KEY (
                    conversation_id
                )
                REFERENCES conversations(id)
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


class ShowMemoryHandlerTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

        self.database_path = (
            Path(
                self.temp_directory.name
            )
            / "test_show_memory.db"
        )

        database.set_database_path(
            self.database_path
        )

        create_test_schema(
            self.database_path
        )

        self.handler = (
            ShowMemoryHandler()
        )

    def tearDown(
        self,
    ):

        self.temp_directory.cleanup()

    def _insert_memory(
        self,
        memory_key,
        content,
        category="SKILL",
        status="ACTIVE",
        confidence=0.95,
        importance=0.90,
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    content,
                    category,
                    confidence,
                    "2026-08-27T00:00:00",
                    "2026-08-27T00:00:00",
                    memory_key,
                    importance,
                    status,
                ),
            )

            connection.commit()

            return cursor.lastrowid

        finally:

            connection.close()

    def _insert_evidence(
        self,
        memory_id,
        evidence_text,
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            connection.execute(
                """
                INSERT INTO memory_evidence (
                    memory_id,
                    evidence_text,
                    evidence_type,
                    confidence,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    evidence_text,
                    "DIRECT",
                    0.95,
                    "2026-08-27T00:00:00",
                ),
            )

            connection.commit()

        finally:

            connection.close()

    def test_command_name(
        self,
    ):

        self.assertEqual(
            self.handler.command_name(),
            "SHOW-MEMORY",
        )

    def test_exact_memory_key_can_be_shown(
        self,
    ):

        memory_id = self._insert_memory(
            memory_key="pcvue_skill",
            content=(
                "User is actively learning PCVUE v17."
            ),
        )

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("pcvue_skill",),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.metadata["memory_id"],
            memory_id,
        )

        self.assertEqual(
            result.metadata["memory_key"],
            "pcvue_skill",
        )

        self.assertIn(
            "User is actively learning PCVUE v17.",
            result.message,
        )

    def test_evidence_count_is_reported(
        self,
    ):

        memory_id = self._insert_memory(
            memory_key="pcvue_skill",
            content=(
                "User is actively learning PCVUE v17."
            ),
        )

        self._insert_evidence(
            memory_id=memory_id,
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("pcvue_skill",),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.metadata["evidence_count"],
            1,
        )

        self.assertIn(
            "Evidence: 1",
            result.message,
        )

    def test_missing_memory_is_reported(
        self,
    ):

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("does_not_exist",),
        )

        result = self.handler.execute(
            request
        )

        self.assertFalse(
            result.success
        )

        self.assertIn(
            "No memory found",
            result.message,
        )

    def test_missing_argument_is_rejected(
        self,
    ):

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=(),
        )

        result = self.handler.execute(
            request
        )

        self.assertFalse(
            result.success
        )

        self.assertIn(
            "Usage:",
            result.message,
        )

    def test_multiple_arguments_are_rejected(
        self,
    ):

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=(
                "pcvue_skill",
                "extra",
            ),
        )

        result = self.handler.execute(
            request
        )

        self.assertFalse(
            result.success
        )

        self.assertIn(
            "Usage:",
            result.message,
        )

    def test_empty_argument_is_rejected(
        self,
    ):

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("   ",),
        )

        result = self.handler.execute(
            request
        )

        self.assertFalse(
            result.success
        )

        self.assertIn(
            "cannot be empty",
            result.message,
        )

    def test_invalid_request_type_is_rejected(
        self,
    ):

        with self.assertRaises(
            TypeError
        ):

            self.handler.execute(
                "not a request"
            )

    def test_show_memory_does_not_modify_memory(
        self,
    ):

        memory_id = self._insert_memory(
            memory_key="pcvue_skill",
            content=(
                "User is actively learning PCVUE v17."
            ),
        )

        before = self._get_memory_row(
            memory_id
        )

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("pcvue_skill",),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        after = self._get_memory_row(
            memory_id
        )

        self.assertEqual(
            before,
            after,
        )

    def test_semantic_lookup_can_find_memory(
        self,
    ):

        memory_id = self._insert_memory(
            memory_key="pcvue_skill",
            content=(
                "User is actively learning PCVUE v17."
            ),
        )

        request = CommandRequest(
            name="SHOW-MEMORY",
            arguments=("PCVUE",),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.metadata["memory_id"],
            memory_id,
        )

    def _get_memory_row(
        self,
        memory_id,
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            return connection.execute(
                """
                SELECT
                    id,
                    content,
                    category,
                    confidence,
                    importance,
                    status,
                    memory_key
                FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()

        finally:

            connection.close()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )