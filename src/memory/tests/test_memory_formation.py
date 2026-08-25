import sqlite3
import tempfile
import unittest
from pathlib import Path


from src import database
from src.memory.memory_formation import (
    CandidateMemory,
    FormationResult,
    extract_candidates,
    process_turn,
    _normalize_key,
)


def _create_test_schema(database_path):
    """
    Create the minimal database schema required for
    memory formation tests.
    """

    connection = sqlite3.connect(database_path)
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
                REFERENCES memories(id)
        )
    """)

    connection.commit()
    connection.close()


class MemoryFormationExtractionTests(unittest.TestCase):
    """
    Tests for the candidate extraction phase.

    These tests do not touch the database.
    """

    def test_empty_response_produces_no_candidates(self):

        candidates = extract_candidates(
            "Hello",
            "",
        )

        self.assertEqual(candidates, [])

    def test_none_response_produces_no_candidates(self):

        candidates = extract_candidates(
            "Hello",
            None,
        )

        self.assertEqual(candidates, [])

    def test_irrelevant_response_produces_no_candidates(self):

        candidates = extract_candidates(
            "Hello",
            "I can help you with that.",
        )

        self.assertEqual(candidates, [])

    def test_skill_keyword_is_extracted(self):

        candidates = extract_candidates(
            "What do I know?",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].category, "SKILL")

    def test_preference_keyword_is_extracted(self):

        candidates = extract_candidates(
            "What do I like?",
            "User prefers dark mode for all development tools.",
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].category, "PREFERENCE")

    def test_project_keyword_is_extracted(self):

        candidates = extract_candidates(
            "What am I working on?",
            "User is building a personal AI assistant named JARVIS.",
        )

        self.assertEqual(len(candidates), 1)

    def test_goal_keyword_is_extracted(self):

        candidates = extract_candidates(
            "What are my goals?",
            "User wants to build an autonomous coding agent.",
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].category, "GOAL")

    def test_personal_keyword_is_extracted(self):

        candidates = extract_candidates(
            "Tell me about myself.",
            "User works at a SCADA engineering firm.",
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].category,
            "PERSONAL",
        )

    def test_workflow_keyword_is_extracted(self):

        candidates = extract_candidates(
            "How do I work?",
            "User typically tests with unittest before deploying.",
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].category,
            "WORKFLOW",
        )

    def test_short_claims_are_rejected(self):

        candidates = extract_candidates(
            "Hello",
            "User is X.",
        )

        self.assertEqual(candidates, [])

    def test_candidate_has_evidence_text(self):

        candidates = extract_candidates(
            "What do I know?",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertTrue(
            len(candidates[0].evidence_text) > 0,
        )

    def test_candidate_has_memory_key(self):

        candidates = extract_candidates(
            "What do I know?",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertTrue(
            len(candidates[0].memory_key) > 0,
        )

    def test_multiline_response_extracts_multiple(self):

        response = (
            "Based on our conversation:\n"
            "User is learning PCVUE v17 for SCADA development.\n"
            "User prefers Python over Java for scripting.\n"
        )

        candidates = extract_candidates(
            "What do you know about me?",
            response,
        )

        self.assertEqual(len(candidates), 2)

    def test_one_match_per_line(self):
        """
        Even if a line matches multiple rules,
        only one candidate is extracted per line.
        """

        candidates = extract_candidates(
            "What do I do?",
            "User is building and developing a JARVIS system.",
        )

        self.assertEqual(len(candidates), 1)


class NormalizeKeyTests(unittest.TestCase):

    def test_spaces_become_underscores(self):

        self.assertEqual(
            _normalize_key("hello world"),
            "hello_world",
        )

    def test_punctuation_is_removed(self):

        self.assertEqual(
            _normalize_key("user's project."),
            "users_project",
        )

    def test_multiple_underscores_are_collapsed(self):

        self.assertEqual(
            _normalize_key("hello   world"),
            "hello_world",
        )

    def test_case_is_lowered(self):

        self.assertEqual(
            _normalize_key("HELLO WORLD"),
            "hello_world",
        )


class MemoryFormationPipelineTests(unittest.TestCase):
    """
    End-to-end tests for the full formation pipeline.

    These tests use a temporary database.
    """

    def setUp(self):

        self.temp_directory = tempfile.TemporaryDirectory()

        self.database_path = (
            Path(self.temp_directory.name) / "test_formation.db"
        )

        database.set_database_path(self.database_path)

        _create_test_schema(self.database_path)

    def tearDown(self):

        self.temp_directory.cleanup()

    def test_process_turn_returns_formation_result(self):

        result = process_turn(
            "What do I know?",
            "I can help you with that.",
        )

        self.assertIsInstance(result, FormationResult)

    def test_irrelevant_turn_creates_no_memories(self):

        result = process_turn(
            "Hello",
            "Hi there, how can I help?",
        )

        self.assertEqual(result.candidates_extracted, 0)
        self.assertEqual(result.memories_created, 0)

    def test_relevant_turn_creates_memory(self):

        result = process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertEqual(result.candidates_extracted, 1)
        self.assertEqual(result.memories_created, 1)

    def test_memory_is_persisted_to_database(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM memories"
        )

        count = cursor.fetchone()[0]

        connection.close()

        self.assertEqual(count, 1)

    def test_evidence_is_persisted(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM memory_evidence"
        )

        count = cursor.fetchone()[0]

        connection.close()

        self.assertEqual(count, 1)

    def test_evidence_is_linked_to_memory(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                e.memory_id,
                m.id
            FROM memory_evidence e
            JOIN memories m ON e.memory_id = m.id
        """)

        row = cursor.fetchone()

        connection.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], row[1])

    def test_duplicate_turn_deduplicates(self):

        first_result = process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        second_result = process_turn(
            "I'm still studying PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertEqual(first_result.memories_created, 1)

        self.assertEqual(second_result.memories_created, 0)
        self.assertEqual(
            second_result.memories_deduplicated, 1,
        )

    def test_deduplicated_turn_adds_corroborating_evidence(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        result = process_turn(
            "I'm still studying PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertEqual(result.evidence_added, 1)

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT evidence_type
            FROM memory_evidence
            ORDER BY id
        """)

        rows = cursor.fetchall()

        connection.close()

        # First evidence is DIRECT, second is CORROBORATING.
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "DIRECT")
        self.assertEqual(rows[1][0], "CORROBORATING")

    def test_conversation_id_is_stored_in_evidence(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
            conversation_id="conv-test-001",
        )

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT conversation_id
            FROM memory_evidence
        """)

        row = cursor.fetchone()

        connection.close()

        self.assertEqual(row[0], "conv-test-001")

    def test_multiple_candidates_in_one_turn(self):

        response = (
            "Based on our conversation:\n"
            "User is learning PCVUE v17 for SCADA development.\n"
            "User prefers Python over Java for scripting.\n"
        )

        result = process_turn(
            "Tell me what you know.",
            response,
        )

        self.assertEqual(result.candidates_extracted, 2)
        self.assertEqual(result.memories_created, 2)

    def test_formation_result_has_details(self):

        result = process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        self.assertEqual(len(result.details), 1)
        self.assertEqual(
            result.details[0]["action"],
            "created",
        )

    def test_memory_category_is_stored(self):

        process_turn(
            "I'm learning PCVUE.",
            "User is learning PCVUE v17 for SCADA development.",
        )

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT category FROM memories"
        )

        row = cursor.fetchone()

        connection.close()

        self.assertEqual(row[0], "SKILL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
