import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.memory.memory_decision_executor import (
    MemoryDecisionExecutor,
)

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
    MemoryDecision,
)

from src.memory.memory_execution_models import (
    FAILED,
    NO_OP,
    SUCCESS,
)

from src.memory.memory_models import (
    CandidateMemory,
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


class MemoryDecisionExecutorTests(
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
            / "test_executor.db"
        )

        database.set_database_path(
            self.database_path
        )

        create_test_schema(
            self.database_path
        )

        self.executor = (
            MemoryDecisionExecutor()
        )

        self.candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

    def tearDown(
        self,
    ):

        self.temp_directory.cleanup()

    # -------------------------------------------------------------
    # Database test helpers
    # -------------------------------------------------------------

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

    def _insert_memory(
        self,
        content,
        memory_key,
        category="SKILL",
        status="ACTIVE",
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
                    0.95,
                    "2026-08-26T00:00:00",
                    "2026-08-26T00:00:00",
                    memory_key,
                    0.90,
                    status,
                ),
            )

            connection.commit()

            return cursor.lastrowid

        finally:
            connection.close()

    def _decision(
        self,
        action,
        memory_id=None,
        candidate=None,
    ):
        return MemoryDecision(
            action=action,
            candidate=(
                candidate
                or self.candidate
            ),
            memory_id=memory_id,
            reason="Test decision.",
            confidence=0.90,
        )

    # -------------------------------------------------------------
    # IGNORE
    # -------------------------------------------------------------

    def test_ignore_performs_no_operation(
        self,
    ):

        decision = self._decision(
            IGNORE
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            NO_OP,
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

    # -------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------

    def test_create_creates_memory(
        self,
    ):

        decision = self._decision(
            CREATE
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        self.assertIsNotNone(
            result.memory_id
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

    def test_create_adds_direct_evidence(
        self,
    ):

        decision = self._decision(
            CREATE
        )

        result = self.executor.execute(
            decision
        )

        evidence = self._query_one(
            """
            SELECT
                memory_id,
                evidence_text,
                evidence_type
            FROM memory_evidence
            """
        )

        self.assertEqual(
            evidence,
            (
                result.memory_id,
                "I'm learning PCVUE v17.",
                "DIRECT",
            ),
        )

    # -------------------------------------------------------------
    # CONFIRM
    # -------------------------------------------------------------

    def test_confirm_adds_repeated_evidence(
        self,
    ):

        memory_id = self._insert_memory(
            "User is learning PCVUE v17.",
            "pcvue_v17_skill",
        )

        decision = self._decision(
            CONFIRM,
            memory_id=memory_id,
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        evidence_type = self._query_one(
            """
            SELECT evidence_type
            FROM memory_evidence
            """
        )[0]

        self.assertEqual(
            evidence_type,
            "REPEATED",
        )

    # -------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------

    def test_update_changes_memory_content(
        self,
    ):

        memory_id = self._insert_memory(
            "User is learning PCVUE.",
            "pcvue_skill",
        )

        candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        decision = self._decision(
            UPDATE,
            memory_id=memory_id,
            candidate=candidate,
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        row = self._query_one(
            """
            SELECT content
            FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        )

        self.assertEqual(
            row[0],
            "User is learning PCVUE v17.",
        )

    def test_update_preserves_memory_key(
        self,
    ):

        memory_id = self._insert_memory(
            "User is learning PCVUE.",
            "pcvue_skill",
        )

        candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        decision = self._decision(
            UPDATE,
            memory_id=memory_id,
            candidate=candidate,
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        row = self._query_one(
            """
            SELECT memory_key
            FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        )

        self.assertEqual(
            row[0],
            "pcvue_skill",
        )

    def test_update_adds_repeated_evidence(
        self,
    ):

        memory_id = self._insert_memory(
            "User is learning PCVUE.",
            "pcvue_skill",
        )

        candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        decision = self._decision(
            UPDATE,
            memory_id=memory_id,
            candidate=candidate,
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        row = self._query_one(
            """
            SELECT
                evidence_type,
                evidence_text
            FROM memory_evidence
            """
        )

        self.assertEqual(
            row,
            (
                "REPEATED",
                "I'm learning PCVUE v17.",
            ),
        )

    # -------------------------------------------------------------
    # CONTRADICT
    # -------------------------------------------------------------

    def _create_qsc_contradiction(
        self,
    ):

        old_id = self._insert_memory(
            "User works at QSC.",
            "qsc_work",
            category="FACT",
        )

        candidate = CandidateMemory(
            content=(
                "User no longer works at QSC."
            ),
            category="FACT",
            memory_key="qsc_work",
            subject="works at QSC",
            evidence_text=(
                "I no longer work at QSC."
            ),
        )

        decision = self._decision(
            CONTRADICT,
            memory_id=old_id,
            candidate=candidate,
        )

        return (
            old_id,
            decision,
        )

    def test_contradiction_supersedes_old_memory(
        self,
    ):

        old_id, decision = (
            self._create_qsc_contradiction()
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        old_status = self._query_one(
            """
            SELECT status
            FROM memories
            WHERE id = ?
            """,
            (old_id,),
        )[0]

        self.assertEqual(
            old_status,
            "SUPERSEDED",
        )

    def test_contradiction_creates_new_active_memory(
        self,
    ):

        old_id, decision = (
            self._create_qsc_contradiction()
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            SUCCESS,
        )

        self.assertIsNotNone(
            result.memory_id
        )

        self.assertNotEqual(
            result.memory_id,
            old_id,
        )

        new_status = self._query_one(
            """
            SELECT status
            FROM memories
            WHERE id = ?
            """,
            (result.memory_id,),
        )[0]

        self.assertEqual(
            new_status,
            "ACTIVE",
        )

    def test_contradiction_adds_direct_evidence_to_replacement(
        self,
    ):

        old_id, decision = (
            self._create_qsc_contradiction()
        )

        result = self.executor.execute(
            decision
        )

        evidence = self._query_one(
            """
            SELECT
                memory_id,
                evidence_type,
                evidence_text
            FROM memory_evidence
            """
        )

        self.assertEqual(
            evidence,
            (
                result.memory_id,
                "DIRECT",
                "I no longer work at QSC.",
            ),
        )

    # -------------------------------------------------------------
    # Invalid execution conditions
    # -------------------------------------------------------------

    def test_missing_memory_id_fails_confirm(
        self,
    ):

        decision = self._decision(
            CONFIRM
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            FAILED,
        )

    def test_missing_memory_id_fails_update(
        self,
    ):

        decision = self._decision(
            UPDATE
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            FAILED,
        )

    def test_missing_memory_id_fails_contradict(
        self,
    ):

        decision = self._decision(
            CONTRADICT
        )

        result = self.executor.execute(
            decision
        )

        self.assertEqual(
            result.status,
            FAILED,
        )

    def test_non_decision_input_is_rejected(
        self,
    ):

        with self.assertRaises(
            TypeError
        ):

            self.executor.execute(
                "not a decision"
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )