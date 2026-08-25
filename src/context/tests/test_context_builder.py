import sqlite3
import tempfile
import unittest
from pathlib import Path
from src.core.conversation import ConversationState

from src import database

from src.context.context_builder import (
    build_context,
)

from src.context.models import (
    ContextItem,
    ContextOptions,
    MEMORY,
    EVIDENCE,
    HISTORY,
    STATE,
    PRIVATE,
)


class ContextBuilderTests(unittest.TestCase):

    def setUp(self):

        self.original_database_path = (
            database.DATABASE_PATH
        )

        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

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
                'conversation-002',
                'message-002',
                'User discusses progressing through PCVUE v17.',
                'CORROBORATING',
                0.90,
                '2026-08-16T10:00:00',
                '2026-08-16T12:00:00'
            )
        """)

        connection.commit()
        connection.close()

    def tearDown(self):

        database.set_database_path(
            self.original_database_path
        )

        self.temp_directory.cleanup()

    def test_builds_context_from_memory(self):

        context = build_context(
            "PCVUE"
        )

        self.assertEqual(
            context.request,
            "PCVUE"
        )

        memories = [
            item
            for item in context.items
            if item.source_type == MEMORY
        ]

        self.assertEqual(
            len(memories),
            1
        )

        self.assertEqual(
            memories[0].provenance["memory_key"],
            "pcvue_skill"
        )

    def test_evidence_is_included(self):

        context = build_context(
            "PCVUE"
        )

        evidence = [
            item
            for item in context.items
            if item.source_type == EVIDENCE
        ]

        self.assertEqual(
            len(evidence),
            2
        )

    def test_evidence_limit_is_respected(self):

        options = ContextOptions(
            max_evidence=1
        )

        context = build_context(
            "PCVUE",
            options=options
        )

        evidence = [
            item
            for item in context.items
            if item.source_type == EVIDENCE
        ]

        self.assertEqual(
            len(evidence),
            1
        )

    def test_memory_limit_is_respected(self):

        options = ContextOptions(
            max_memories=0
        )

        context = build_context(
            "PCVUE",
            options=options
        )

        memories = [
            item
            for item in context.items
            if item.source_type == MEMORY
        ]

        self.assertEqual(
            len(memories),
            0
        )

    def test_empty_query_produces_empty_context(self):

        context = build_context("")

        self.assertEqual(
            context.items,
            ()
        )

    def test_no_results_produces_empty_context(self):

        context = build_context(
            "quantum_bananas"
        )

        self.assertEqual(
            context.items,
            ()
        )

    def test_provenance_is_preserved(self):

        context = build_context(
            "PCVUE"
        )

        memory = next(
            item
            for item in context.items
            if item.source_type == MEMORY
        )

        evidence = next(
            item
            for item in context.items
            if item.source_type == EVIDENCE
        )

        self.assertEqual(
            memory.provenance["memory_id"],
            1
        )

        self.assertEqual(
            memory.provenance["memory_key"],
            "pcvue_skill"
        )

        self.assertEqual(
            evidence.provenance["memory_id"],
            1
        )

        self.assertEqual(
            evidence.provenance["conversation_id"],
            "conversation-001"
        )

        self.assertEqual(
            evidence.provenance["message_id"],
            "message-001"
        )

    def test_privacy_metadata_is_preserved(self):

        context = build_context(
            "PCVUE"
        )

        for item in context.items:

            self.assertEqual(
                item.privacy_level,
                PRIVATE
            )

    def test_history_can_be_supplied(self):

        history_items = [
            {
                "content": "We discussed PCVUE yesterday.",
                "relevance_score": 0.8,
                "privacy_level": PRIVATE,
                "provenance": {
                    "conversation_id": "conversation-003"
                },
            }
        ]

        options = ContextOptions(
            include_memories=False,
            include_evidence=False,
            include_history=True,
            max_history=1,
        )

        context = build_context(
            "PCVUE",
            options=options,
            history_items=history_items,
        )

        history = [
            item
            for item in context.items
            if item.source_type == HISTORY
        ]

        self.assertEqual(
            len(history),
            1
        )

        self.assertEqual(
            history[0].provenance[
                "conversation_id"
            ],
            "conversation-003"
        )

    def test_history_limit_is_respected(self):

        history_items = [
            {"content": "History A"},
            {"content": "History B"},
            {"content": "History C"},
        ]

        options = ContextOptions(
            include_memories=False,
            include_evidence=False,
            include_history=True,
            max_history=2,
        )

        context = build_context(
            "PCVUE",
            options=options,
            history_items=history_items,
        )

        history = [
            item
            for item in context.items
            if item.source_type == HISTORY
        ]

        self.assertEqual(
            len(history),
            2
        )

    def test_context_is_deterministic(self):

        first = build_context(
            "PCVUE"
        )

        second = build_context(
            "PCVUE"
        )

        self.assertEqual(
            first,
            second
        )

    def test_context_building_does_not_modify_database(self):

        connection = database.get_connection()

        before_memory_count = connection.execute(
            "SELECT COUNT(*) FROM memories"
        ).fetchone()[0]

        before_evidence_count = connection.execute(
            "SELECT COUNT(*) FROM memory_evidence"
        ).fetchone()[0]

        connection.close()

        build_context("PCVUE")

        connection = database.get_connection()

        after_memory_count = connection.execute(
            "SELECT COUNT(*) FROM memories"
        ).fetchone()[0]

        after_evidence_count = connection.execute(
            "SELECT COUNT(*) FROM memory_evidence"
        ).fetchone()[0]

        connection.close()

        self.assertEqual(
            before_memory_count,
            after_memory_count
        )

        self.assertEqual(
            before_evidence_count,
            after_evidence_count
        )

    def test_context_does_not_contain_provider_specific_objects(self):

        context = build_context(
            "PCVUE"
        )

        self.assertNotIn(
            "OpenAI",
            str(context)
        )

        self.assertNotIn(
            "ChatCompletion",
            str(context)
        )

    def test_state_is_included(self):
        conversation = ConversationState()

        conversation.set_topic(
            "PCVUE troubleshooting"
        )

        conversation.set_task(
            "Find the cause of the Modbus issue."
        )

        conversation.add_turn(
            "user",
            "The value is stuck at 99.4."
        )

        snapshot = conversation.snapshot()

        context = build_context(
            "Why is this happening?",
            state_snapshot=snapshot,
        )

        state_items = [
            item
            for item in context.items
            if item.source_type == STATE
        ]

        self.assertGreaterEqual(
            len(state_items),
            3
        )

    def test_state_provenance_is_preserved(self):
        conversation = ConversationState(
            conversation_id="state-test"
        )

        conversation.set_topic(
            "Modbus troubleshooting"
        )

        snapshot = conversation.snapshot()

        context = build_context(
            "What are we working on?",
            state_snapshot=snapshot,
        )

        state_item = next(
            item
            for item in context.items
            if item.source_type == STATE
        )

        self.assertEqual(
            state_item.provenance[
                "conversation_id"
            ],
            "state-test"
        )

    def test_state_uses_recent_turns(self):

        conversation = ConversationState()

        for number in range(1, 6):
            conversation.add_turn(
                "user",
                f"Message {number}"
            )

        snapshot = conversation.snapshot()

        options = ContextOptions(
            max_state_turns=2
        )

        context = build_context(
            "What was recent?",
            options=options,
            state_snapshot=snapshot,
        )

        state_items = [
            item
            for item in context.items
            if item.source_type == STATE
        ]

        state_text = [
            item.content
            for item in state_items
        ]

        self.assertEqual(
            len(state_items),
            2
        )

        self.assertIn(
            "Message 4",
            state_text[0]
        )

        self.assertIn(
            "Message 5",
            state_text[1]
        )

    def test_state_preserves_topic_and_task_with_recent_turn_limit(self):

        conversation = ConversationState()

        conversation.set_topic(
            "Modbus troubleshooting"
        )

        conversation.set_task(
            "Find the cause of the register issue."
        )

        for number in range(1, 5):
            conversation.add_turn(
                "user",
                f"Message {number}"
            )

        snapshot = conversation.snapshot()

        options = ContextOptions(
            max_state_turns=1
        )

        context = build_context(
            "Continue troubleshooting.",
            options=options,
            state_snapshot=snapshot,
        )

        state_items = [
            item
            for item in context.items
            if item.source_type == STATE
        ]

        self.assertEqual(
            len(state_items),
            3
        )

        state_text = "\n".join(
            item.content
            for item in state_items
        )

        self.assertIn(
            "Modbus troubleshooting",
            state_text
        )

        self.assertIn(
            "Find the cause of the register issue.",
            state_text
        )

        self.assertIn(
            "Message 4",
            state_text
        )

    def test_zero_state_turns_preserves_topic_and_task(self):

        conversation = ConversationState()

        conversation.set_topic(
            "PCVUE"
        )

        conversation.set_task(
            "Learn the HMI workflow."
        )

        conversation.add_turn(
            "user",
            "This turn should not be included."
        )

        snapshot = conversation.snapshot()

        options = ContextOptions(
            max_state_turns=0
        )

        context = build_context(
            "What are we doing?",
            options=options,
            state_snapshot=snapshot,
        )

        state_items = [
            item
            for item in context.items
            if item.source_type == STATE
        ]

        self.assertEqual(
            len(state_items),
            2
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)