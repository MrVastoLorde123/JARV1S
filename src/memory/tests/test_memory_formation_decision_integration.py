import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.memory.memory_decision import (
    MemoryDecisionService,
)

from src.memory.memory_decision_executor import (
    MemoryDecisionExecutor,
)

from src.memory.providers.deterministic_memory_decision import (
    DeterministicMemoryDecisionProvider,
)

from src.memory.memory_formation import (
    process_turn,
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
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT,
                parent_id TEXT,

                FOREIGN KEY (
                    conversation_id
                )
                REFERENCES conversations(id)
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
                REFERENCES conversations(id),

                FOREIGN KEY (
                    message_id
                )
                REFERENCES messages(id)
            )
            """
        )

        connection.commit()

    finally:

        connection.close()


class MemoryFormationDecisionIntegrationTests(
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
            / "test_integration.db"
        )

        database.set_database_path(
            self.database_path
        )

        create_test_schema(
            self.database_path
        )

        self.decision_service = (
            MemoryDecisionService(
                default_provider="deterministic"
            )
        )

        self.decision_service.register_provider(
            DeterministicMemoryDecisionProvider()
        )

        self.executor = (
            MemoryDecisionExecutor()
        )

    def tearDown(
        self,
    ):

        self.temp_directory.cleanup()

    def _query_one(
        self,
        query,
        parameters=(),
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            return connection.execute(
                query,
                parameters,
            ).fetchone()

        finally:

            connection.close()

    def _query_all(
        self,
        query,
        parameters=(),
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            return connection.execute(
                query,
                parameters,
            ).fetchall()

        finally:

            connection.close()

    def _insert_conversation(
        self,
        conversation_id="conversation-001",
    ):

        self._query_one(
            """
            SELECT 1
            """
        )

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            connection.execute(
                """
                INSERT INTO conversations (
                    id
                )
                VALUES (?)
                """,
                (
                    conversation_id,
                ),
            )

            connection.commit()

        finally:

            connection.close()

    def _insert_message(
        self,
        message_id,
        conversation_id,
        content,
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        try:

            connection.execute(
                """
                INSERT INTO messages (
                    id,
                    conversation_id,
                    role,
                    content,
                    created_at,
                    parent_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    "user",
                    content,
                    "2026-08-26T00:00:00",
                    None,
                ),
            )

            connection.commit()

        finally:

            connection.close()

    def test_new_candidate_is_created_through_decision_stack(
        self,
    ):

        self._insert_conversation()

        self._insert_message(
            message_id="message-001",
            conversation_id="conversation-001",
            content=(
                "I'm learning PCVUE v17."
            ),
        )

        result = process_turn(
            user_query=(
                "I'm learning PCVUE v17."
            ),
            assistant_response=(
                "Understood."
            ),
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-001",
            source_created_at=(
                "2026-08-26T00:00:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            result.candidates_extracted,
            1,
        )

        self.assertEqual(
            result.memories_created,
            1,
        )

        self.assertEqual(
            result.evidence_added,
            1,
        )

        row = self._query_one(
            """
            SELECT
                content,
                category,
                status
            FROM memories
            """
        )

        self.assertEqual(
            row,
            (
                "User is learning PCVUE v17.",
                "SKILL",
                "ACTIVE",
            ),
        )

    def test_existing_candidate_is_confirmed(
        self,
    ):

        self._insert_conversation()

        self._insert_message(
            message_id="message-001",
            conversation_id="conversation-001",
            content=(
                "I'm learning PCVUE v17."
            ),
        )

        first = process_turn(
            user_query=(
                "I'm learning PCVUE v17."
            ),
            assistant_response="Okay.",
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-001",
            source_created_at=(
                "2026-08-26T00:00:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            first.memories_created,
            1,
        )

        self._insert_message(
            message_id="message-002",
            conversation_id="conversation-001",
            content=(
                "I'm still learning PCVUE v17."
            ),
        )

        second = process_turn(
            user_query=(
                "I'm still learning PCVUE v17."
            ),
            assistant_response="Good.",
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-002",
            source_created_at=(
                "2026-08-26T00:01:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            second.memories_created,
            0,
        )

        self.assertEqual(
            second.memories_deduplicated,
            1,
        )

        evidence_rows = self._query_all(
            """
            SELECT
                evidence_type,
                evidence_text
            FROM memory_evidence
            ORDER BY id
            """
        )

        self.assertEqual(
            len(evidence_rows),
            2,
        )

        self.assertEqual(
            evidence_rows[1],
            (
                "REPEATED",
                "I'm still learning PCVUE v17.",
            ),
        )

    def test_more_specific_candidate_updates_existing_memory(
        self,
    ):

        self._insert_conversation()

        self._insert_message(
            message_id="message-001",
            conversation_id="conversation-001",
            content=(
                "I'm learning PCVUE."
            ),
        )

        first = process_turn(
            user_query=(
                "I'm learning PCVUE."
            ),
            assistant_response="Okay.",
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-001",
            source_created_at=(
                "2026-08-26T00:00:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            first.memories_created,
            1,
        )

        self._insert_message(
            message_id="message-002",
            conversation_id="conversation-001",
            content=(
                "I'm learning PCVUE v17."
            ),
        )

        second = process_turn(
            user_query=(
                "I'm learning PCVUE v17."
            ),
            assistant_response="Good.",
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-002",
            source_created_at=(
                "2026-08-26T00:01:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            second.memories_updated,
            1,
        )

        row = self._query_one(
            """
            SELECT content
            FROM memories
            WHERE status = 'ACTIVE'
            """
        )

        self.assertEqual(
            row[0],
            "User is learning PCVUE v17.",
        )

    def test_irrelevant_candidate_is_ignored_without_mutation(
        self,
    ):

        self._insert_conversation()

        self._insert_message(
            message_id="message-001",
            conversation_id="conversation-001",
            content=(
                "I'm building a house."
            ),
        )

        result = process_turn(
            user_query=(
                "I'm building a house."
            ),
            assistant_response="Okay.",
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-001",
            source_created_at=(
                "2026-08-26T00:00:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        self.assertEqual(
            result.memories_created,
            1,
        )

        self.assertEqual(
            result.memories_updated,
            0,
        )

    def test_assistant_response_is_not_used_as_memory_evidence(
        self,
    ):

        self._insert_conversation()

        self._insert_message(
            message_id="message-001",
            conversation_id="conversation-001",
            content=(
                "I'm learning PCVUE v17."
            ),
        )

        process_turn(
            user_query=(
                "I'm learning PCVUE v17."
            ),
            assistant_response=(
                "You are an expert in PCVUE."
            ),
            conversation_id=(
                "conversation-001"
            ),
            message_id="message-001",
            source_created_at=(
                "2026-08-26T00:00:00"
            ),
            decision_service=(
                self.decision_service
            ),
            executor=self.executor,
        )

        evidence_text = self._query_one(
            """
            SELECT evidence_text
            FROM memory_evidence
            """
        )[0]

        self.assertEqual(
            evidence_text,
            "I'm learning PCVUE v17.",
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )