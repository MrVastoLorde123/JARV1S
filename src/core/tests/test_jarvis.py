import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.ai.models import (
    AIResponse,
    AICapabilities,
    AIRequest,
)

from src.ai.provider import AIProvider
from src.ai.service import AIService

from src.context.models import (
    ContextOptions,
)

from src.core.jarvis import JARVIS
from src.core.models import JARVISResponse


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


class FakeAIProvider(
    AIProvider
):

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        return AIResponse(
            content=(
                "Fake JARVIS response."
            ),
            provider="fake",
            model="fake-model",
            finish_reason="completed",
        )

    def capabilities(
        self,
    ):

        return AICapabilities(
            text_generation=True,
        )

    def provider_name(
        self,
    ):

        return "fake"


class MemoryExtractingFakeProvider(
    AIProvider
):

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        return AIResponse(
            content=(
                "I understand that you "
                "are learning PCVUE."
            ),
            provider="fake",
            model="fake-model",
        )

    def capabilities(
        self,
    ):

        return AICapabilities(
            text_generation=True,
        )

    def provider_name(
        self,
    ):

        return "fake"


class JARVISTests(
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
            / "test_jarvis.db"
        )

        database.set_database_path(
            self.database_path
        )

        _create_test_schema(
            self.database_path
        )

        self.ai_service = AIService(
            default_provider="fake"
        )

        self.ai_service.register_provider(
            FakeAIProvider()
        )

        self.jarvis = JARVIS(
            ai_service=self.ai_service
        )

    def tearDown(
        self,
    ):

        self.temp_directory.cleanup()

    def test_jarvis_returns_jarvis_response(
        self,
    ):

        response = self.jarvis.ask(
            "Hello JARVIS."
        )

        self.assertIsInstance(
            response,
            JARVISResponse,
        )

    def test_response_content_is_preserved(
        self,
    ):

        response = self.jarvis.ask(
            "Hello JARVIS."
        )

        self.assertEqual(
            response.content,
            "Fake JARVIS response.",
        )

    def test_ai_response_is_preserved(
        self,
    ):

        response = self.jarvis.ask(
            "Hello JARVIS."
        )

        self.assertEqual(
            response.ai_response.provider,
            "fake",
        )

        self.assertEqual(
            response.ai_response.model,
            "fake-model",
        )

    def test_context_is_preserved(
        self,
    ):

        response = self.jarvis.ask(
            "What do you know about me?"
        )

        self.assertIsNotNone(
            response.context
        )

    def test_context_options_are_used(
        self,
    ):

        options = ContextOptions(
            include_memories=False,
            include_evidence=False,
            include_history=False,
            include_state=False,
        )

        jarvis = JARVIS(
            ai_service=self.ai_service,
            context_options=options,
        )

        response = jarvis.ask(
            "Test context."
        )

        self.assertEqual(
            response.context.items,
            (),
        )

    def test_provider_can_be_overridden(
        self,
    ):

        second_provider = (
            FakeAIProvider()
        )

        self.ai_service.register_provider(
            second_provider
        )

        response = self.jarvis.ask(
            "Test provider.",
            provider_name="fake",
        )

        self.assertEqual(
            response.ai_response.provider,
            "fake",
        )

    def test_empty_query_is_rejected(
        self,
    ):

        with self.assertRaises(
            ValueError
        ):

            self.jarvis.ask("")

    def test_whitespace_query_is_rejected(
        self,
    ):

        with self.assertRaises(
            ValueError
        ):

            self.jarvis.ask("   ")

    def test_non_string_query_is_rejected(
        self,
    ):

        with self.assertRaises(
            TypeError
        ):

            self.jarvis.ask(123)

    def test_response_metadata_is_present(
        self,
    ):

        response = self.jarvis.ask(
            "Test metadata."
        )

        self.assertEqual(
            response.metadata["provider"],
            "fake",
        )

        self.assertEqual(
            response.metadata["model"],
            "fake-model",
        )

        self.assertIn(
            "context_items",
            response.metadata,
        )

    def test_user_turn_is_recorded(
        self,
    ):

        self.jarvis.ask(
            "Hello JARVIS."
        )

        turns = (
            self.jarvis.conversation
            .get_recent_turns()
        )

        self.assertEqual(
            len(turns),
            2,
        )

        self.assertEqual(
            turns[0].role,
            "user",
        )

        self.assertEqual(
            turns[0].content,
            "Hello JARVIS.",
        )

    def test_assistant_turn_is_recorded(
        self,
    ):

        self.jarvis.ask(
            "Hello JARVIS."
        )

        turns = (
            self.jarvis.conversation
            .get_recent_turns()
        )

        self.assertEqual(
            turns[1].role,
            "assistant",
        )

        self.assertEqual(
            turns[1].content,
            "Fake JARVIS response.",
        )

    def test_conversation_id_is_returned(
        self,
    ):

        response = self.jarvis.ask(
            "Hello JARVIS."
        )

        self.assertEqual(
            response.metadata[
                "conversation_id"
            ],
            (
                self.jarvis
                .conversation
                .conversation_id
            ),
        )

    def test_state_can_be_disabled(
        self,
    ):

        options = ContextOptions(
            include_state=False,
        )

        jarvis = JARVIS(
            ai_service=self.ai_service,
            context_options=options,
        )

        response = jarvis.ask(
            "Test state."
        )

        state_items = [
            item
            for item in response.context.items
            if item.source_type == "STATE"
        ]

        self.assertEqual(
            state_items,
            [],
        )

    def test_conversation_state_carries_previous_turns(
        self,
    ):

        self.jarvis.ask(
            "I'm troubleshooting a Modbus pump issue."
        )

        second_response = self.jarvis.ask(
            "What should I check first?"
        )

        state_items = [
            item
            for item in second_response.context.items
            if item.source_type == "STATE"
        ]

        state_text = "\n".join(
            item.content
            for item in state_items
        )

        self.assertIn(
            (
                "I'm troubleshooting a "
                "Modbus pump issue."
            ),
            state_text,
        )

        self.assertIn(
            "Fake JARVIS response.",
            state_text,
        )

    def test_memory_formation_is_disabled_by_default(
        self,
    ):

        response = self.jarvis.ask(
            "I'm learning PCVUE."
        )

        self.assertNotIn(
            "memory_formation",
            response.metadata,
        )

        memory_count = (
            sqlite3.connect(
                self.database_path
            )
            .execute(
                "SELECT COUNT(*) FROM memories"
            )
            .fetchone()[0]
        )

        self.assertEqual(
            memory_count,
            0,
        )

    def test_memory_formation_can_be_enabled(
        self,
    ):

        ai_service = AIService(
            default_provider="fake"
        )

        ai_service.register_provider(
            MemoryExtractingFakeProvider()
        )

        jarvis = JARVIS(
            ai_service=ai_service,
            enable_memory_formation=True,
        )

        response = jarvis.ask(
            "I'm learning PCVUE.",
        )

        self.assertIn(
            "memory_formation",
            response.metadata,
        )

        formation = (
            response.metadata[
                "memory_formation"
            ]
        )

        self.assertEqual(
            formation[
                "candidates_extracted"
            ],
            1,
        )

        self.assertEqual(
            formation[
                "memories_created"
            ],
            1,
        )

        memory_row = (
            sqlite3.connect(
                self.database_path
            )
            .execute(
                """
                SELECT
                    content,
                    category
                FROM memories
                """
            )
            .fetchone()
        )

        self.assertEqual(
            memory_row,
            (
                "User is learning PCVUE.",
                "SKILL",
            ),
        )

    def test_memory_formation_uses_user_statement_as_evidence(
        self,
    ):

        ai_service = AIService(
            default_provider="fake"
        )

        ai_service.register_provider(
            MemoryExtractingFakeProvider()
        )

        jarvis = JARVIS(
            ai_service=ai_service,
            enable_memory_formation=True,
        )

        jarvis.ask(
            "I'm learning PCVUE.",
        )

        evidence_row = (
            sqlite3.connect(
                self.database_path
            )
            .execute(
                """
                SELECT
                    evidence_text,
                    evidence_type
                FROM memory_evidence
                """
            )
            .fetchone()
        )

        self.assertEqual(
            evidence_row,
            (
                "I'm learning PCVUE.",
                "DIRECT",
            ),
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )