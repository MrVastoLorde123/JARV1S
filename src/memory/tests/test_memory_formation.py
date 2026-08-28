import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.memory.memory_formation import (
    FormationResult,
    extract_candidates,
    process_turn,
    _normalize_key,
)

from src.memory.memory_models import (
    CandidateMemory,
)

def _create_test_schema(
    database_path,
):
    connection = sqlite3.connect(
        database_path
    )

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
    connection.close()


class MemoryFormationExtractionTests(
    unittest.TestCase
):

    def test_empty_user_message_produces_no_candidates(
        self,
    ):
        candidates = extract_candidates(
            "",
            "User is learning PCVUE.",
        )

        self.assertEqual(
            candidates,
            [],
        )

    def test_irrelevant_message_produces_no_candidates(
        self,
    ):
        candidates = extract_candidates(
            "Hello, can you help me?",
            "User is learning PCVUE.",
        )

        self.assertEqual(
            candidates,
            [],
        )

    def test_assistant_response_is_not_direct_evidence(
        self,
    ):
        candidates = extract_candidates(
            "Tell me something interesting.",
            "User is learning PCVUE v17.",
        )

        self.assertEqual(
            candidates,
            [],
        )

    def test_skill_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I'm learning PCVUE v17.",
            "Great, PCVUE is useful.",
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "SKILL",
        )

        self.assertEqual(
            candidates[0].content,
            "User is learning PCVUE v17.",
        )

        self.assertEqual(
            candidates[0].evidence_text,
            "I'm learning PCVUE v17.",
        )

        self.assertEqual(
            candidates[0].evidence_type,
            "DIRECT",
        )

    def test_project_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I'm building JARVIS.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "PROJECT",
        )

        self.assertEqual(
            candidates[0].content,
            "User is building JARVIS.",
        )

    def test_preference_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I prefer Python for scripting.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "PREFERENCE",
        )

    def test_goal_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I want to build a JARVIS server.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "GOAL",
        )

    def test_personal_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I live in Suriname.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "PERSONAL",
        )

        self.assertEqual(
            candidates[0].content,
            "User lives in Suriname.",
        )

    def test_workflow_statement_is_extracted(
        self,
    ):
        candidates = extract_candidates(
            "I usually test with unittest.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertEqual(
            candidates[0].category,
            "WORKFLOW",
        )

    def test_multiple_statements_are_extracted(
        self,
    ):
        candidates = extract_candidates(
            (
                "I'm learning PCVUE v17. "
                "I prefer Python for scripting."
            ),
            None,
        )

        self.assertEqual(
            len(candidates),
            2,
        )

    def test_duplicate_candidate_keys_are_removed(
        self,
    ):
        candidates = extract_candidates(
            (
                "I'm learning PCVUE v17. "
                "I'm learning PCVUE v17."
            ),
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

    def test_memory_key_is_normalized(
        self,
    ):
        self.assertEqual(
            _normalize_key(
                "PCVUE v17"
            ),
            "pcvue_v17",
        )


class MemoryFormationPipelineTests(
    unittest.TestCase
):

    def setUp(self):

        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

        self.database_path = (
            Path(
                self.temp_directory.name
            )
            / "test_formation.db"
        )

        database.set_database_path(
            self.database_path
        )

        _create_test_schema(
            self.database_path
        )

    def tearDown(self):

        self.temp_directory.cleanup()

    def _query_one(
        self,
        query,
        parameters=(),
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        row = connection.execute(
            query,
            parameters,
        ).fetchone()

        connection.close()

        return row

    def _query_all(
        self,
        query,
        parameters=(),
    ):

        connection = sqlite3.connect(
            self.database_path
        )

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        connection.close()

        return rows

    def test_result_type(
        self,
    ):
        result = process_turn(
            "Hello.",
            "Hi there.",
        )

        self.assertIsInstance(
            result,
            FormationResult,
        )

    def test_irrelevant_turn_creates_nothing(
        self,
    ):
        result = process_turn(
            "Hello.",
            "Hi there.",
        )

        self.assertEqual(
            result.candidates_extracted,
            0,
        )

        self.assertEqual(
            result.memories_created,
            0,
        )

        self.assertEqual(
            result.evidence_added,
            0,
        )

    def test_user_statement_creates_memory(
        self,
    ):
        result = process_turn(
            "I'm learning PCVUE v17.",
            "That's good.",
        )

        self.assertEqual(
            result.candidates_extracted,
            1,
        )

        self.assertEqual(
            result.memories_created,
            1,
        )

    def test_memory_is_persisted(
        self,
    ):
        process_turn(
            "I'm learning PCVUE v17.",
            "That's good.",
        )

        row = self._query_one(
            """
            SELECT
                memory_key,
                content,
                category,
                status
            FROM memories
            """
        )

        self.assertIsNotNone(
            row
        )

        self.assertEqual(
            row[1],
            "User is learning PCVUE v17.",
        )

        self.assertEqual(
            row[2],
            "SKILL",
        )

        self.assertEqual(
            row[3],
            "ACTIVE",
        )

    def test_direct_user_evidence_is_persisted(
        self,
    ):
        process_turn(
            "I'm learning PCVUE v17.",
            "The assistant says something unrelated.",
        )

        row = self._query_one(
            """
            SELECT
                evidence_text,
                evidence_type
            FROM memory_evidence
            """
        )

        self.assertEqual(
            row[0],
            "I'm learning PCVUE v17.",
        )

        self.assertEqual(
            row[1],
            "DIRECT",
        )

    def test_assistant_claim_is_never_saved_as_direct_evidence(
        self,
    ):
        result = process_turn(
            "Can you help me?",
            "User is learning PCVUE v17.",
        )

        self.assertEqual(
            result.memories_created,
            0,
        )

        count = self._query_one(
            "SELECT COUNT(*) FROM memories"
        )

        self.assertEqual(
            count[0],
            0,
        )

    def test_duplicate_memory_adds_repeated_evidence(
        self,
    ):
        first = process_turn(
            "I'm learning PCVUE v17.",
            "Understood.",
        )

        second = process_turn(
            "I'm still learning PCVUE v17.",
            "Good progress.",
        )

        self.assertEqual(
            first.memories_created,
            1,
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
            evidence_rows[0][0],
            "DIRECT",
        )

        self.assertEqual(
            evidence_rows[1][0],
            "REPEATED",
        )

    def test_existing_pcvue_memory_is_found_semantically(
        self,
    ):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
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
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                "User is actively learning PCVUE v17.",
                "SKILL",
                0.95,
                "2026-08-25T00:00:00",
                "2026-08-25T00:00:00",
                "pcvue_skill",
                0.90,
                "ACTIVE",
            ),
        )

        connection.commit()
        connection.close()

        result = process_turn(
            "I'm learning PCVUE v17.",
            "Understood.",
        )

        self.assertEqual(
            result.memories_created,
            0,
        )

        self.assertEqual(
            result.memories_deduplicated,
            1,
        )

        count = self._query_one(
            "SELECT COUNT(*) FROM memories"
        )

        self.assertEqual(
            count[0],
            1,
        )

    def test_evidence_source_timestamp_is_stored(
        self,
    ):
        process_turn(
            "I'm learning PCVUE v17.",
            "Understood.",
            source_created_at=(
                "2026-08-25T10:00:00+00:00"
            ),
        )

        row = self._query_one(
            """
            SELECT source_created_at
            FROM memory_evidence
            """
        )

        self.assertEqual(
            row[0],
            "2026-08-25T10:00:00+00:00",
        )

    def test_persistent_conversation_id_can_be_stored(
        self,
    ):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
            """
            INSERT INTO conversations (
                id
            )
            VALUES (?)
            """,
            ("conversation-001",),
        )

        connection.commit()
        connection.close()

        result = process_turn(
            "I'm learning PCVUE v17.",
            "Understood.",
            conversation_id=(
                "conversation-001"
            ),
        )

        self.assertEqual(
            result.memories_created,
            1,
        )

        row = self._query_one(
            """
            SELECT conversation_id
            FROM memory_evidence
            """
        )

        self.assertEqual(
            row[0],
            "conversation-001",
        )

    def test_formation_details_are_present(
        self,
    ):
        result = process_turn(
            "I'm learning PCVUE v17.",
            "Understood.",
        )

        self.assertEqual(
            len(result.details),
            1,
        )

        self.assertEqual(
            result.details[0].action,
            "created",
        )

        self.assertIsNotNone(
            result.details[0].memory_id
        )

    def test_validation_rejects_invalid_candidate(
        self,
    ):
        candidates = extract_candidates(
            "I want to build something.",
            None,
        )

        self.assertEqual(
            len(candidates),
            1,
        )

        self.assertTrue(
            candidates[0].content
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )