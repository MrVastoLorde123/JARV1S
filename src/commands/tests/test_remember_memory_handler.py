import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.commands.handlers.memory import (
    RememberMemoryHandler,
)

from src.commands.models import (
    CommandRequest,
)

from src.memory.memory_decision import (
    MemoryDecisionService,
)

from src.memory.memory_decision_executor import (
    MemoryDecisionExecutor,
)

from src.memory.providers.deterministic_memory_decision import (
    DeterministicMemoryDecisionProvider,
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
                parent_id TEXT
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
                status TEXT NOT NULL DEFAULT 'ACTIVE'
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
                REFERENCES memories(id)
            )
            """
        )

        connection.commit()

    finally:

        connection.close()


class RememberMemoryHandlerTests(
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
            / "test_remember.db"
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

        self.handler = (
            RememberMemoryHandler(
                decision_service=(
                    self.decision_service
                ),
                executor=self.executor,
            )
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

    def test_command_name(
        self,
    ):

        self.assertEqual(
            self.handler.command_name(),
            "REMEMBER",
        )

    def test_missing_argument_is_rejected(
        self,
    ):

        request = CommandRequest(
            name="REMEMBER",
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

    def test_empty_statement_is_rejected(
        self,
    ):

        request = CommandRequest(
            name="REMEMBER",
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

    def test_non_string_request_is_rejected(
        self,
    ):

        with self.assertRaises(
            TypeError
        ):

            self.handler.execute(
                "not a request"
            )

    def test_explicit_remember_creates_memory(
        self,
    ):

        request = CommandRequest(
            name="REMEMBER",
            arguments=(
                "I prefer local AI",
            ),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        self.assertIsNotNone(
            result.metadata["memory_id"]
        )

        row = self._query_one(
            """
            SELECT
                content,
                category,
                status,
                confidence,
                importance
            FROM memories
            """
        )

        self.assertEqual(
            row[0],
            "I prefer local AI",
        )

        self.assertEqual(
            row[1],
            "FACT",
        )

        self.assertEqual(
            row[2],
            "ACTIVE",
        )

        self.assertEqual(
            row[3],
            1.0,
        )

        self.assertEqual(
            row[4],
            0.75,
        )

    def test_explicit_remember_creates_direct_evidence(
        self,
    ):

        request = CommandRequest(
            name="REMEMBER",
            arguments=(
                "I prefer local AI",
            ),
        )

        result = self.handler.execute(
            request
        )

        evidence = self._query_one(
            """
            SELECT
                memory_id,
                evidence_text,
                evidence_type,
                confidence
            FROM memory_evidence
            """
        )

        self.assertEqual(
            evidence[0],
            result.metadata["memory_id"],
        )

        self.assertEqual(
            evidence[1],
            "I prefer local AI",
        )

        self.assertEqual(
            evidence[2],
            "DIRECT",
        )

        self.assertEqual(
            evidence[3],
            1.0,
        )

    def test_multiple_arguments_become_one_statement(
        self,
    ):

        request = CommandRequest(
            name="REMEMBER",
            arguments=(
                "I",
                "prefer",
                "local",
                "AI",
            ),
        )

        result = self.handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        content = self._query_one(
            """
            SELECT content
            FROM memories
            """
        )[0]

        self.assertEqual(
            content,
            "I prefer local AI",
        )

    def test_no_memory_is_created_on_failed_decision(
        self,
    ):

        class RejectingDecisionService:

            def decide(
                self,
                context,
                provider_name=None,
            ):

                from src.memory.memory_decision_models import (
                    IGNORE,
                    MemoryDecision,
                )

                return MemoryDecision(
                    action=IGNORE,
                    candidate=context.candidate,
                    memory_id=None,
                    reason="Rejected for test.",
                    confidence=0.99,
                )

        handler = RememberMemoryHandler(
            decision_service=(
                RejectingDecisionService()
            ),
            executor=self.executor,
        )

        request = CommandRequest(
            name="REMEMBER",
            arguments=(
                "I prefer local AI",
            ),
        )

        result = handler.execute(
            request
        )

        self.assertFalse(
            result.success
        )

        count = self._query_one(
            """
            SELECT COUNT(*)
            FROM memories
            """
        )[0]

        self.assertEqual(
            count,
            0,
        )

    def test_memory_write_occurs_through_executor(
        self,
    ):

        class RecordingExecutor:

            def __init__(
                self,
            ):
                self.received_decision = None

            def execute(
                self,
                decision,
                conversation_id=None,
                message_id=None,
                source_created_at=None,
            ):
                self.received_decision = (
                    decision
                )

                from src.memory.memory_execution_models import (
                    SUCCESS,
                    MemoryExecutionResult,
                )

                return MemoryExecutionResult(
                    status=SUCCESS,
                    action=decision.action,
                    memory_id=123,
                    evidence_id=456,
                    reason="Recorded.",
                )

        executor = RecordingExecutor()

        handler = RememberMemoryHandler(
            decision_service=(
                self.decision_service
            ),
            executor=executor,
        )

        request = CommandRequest(
            name="REMEMBER",
            arguments=(
                "I prefer local AI",
            ),
        )

        result = handler.execute(
            request
        )

        self.assertTrue(
            result.success
        )

        self.assertIsNotNone(
            executor.received_decision
        )

        self.assertEqual(
            executor.received_decision.action,
            "CREATE",
        )

        count = self._query_one(
            """
            SELECT COUNT(*)
            FROM memories
            """
        )[0]

        self.assertEqual(
            count,
            0,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )