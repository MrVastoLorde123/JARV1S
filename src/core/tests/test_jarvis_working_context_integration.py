import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database
from src.ai.models import AIResponse, AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.context.context_source_provider import ContextSourceProvider
from src.context.context_source_selection import ContextSource
from src.context.memory_context_source_provider import MemoryContextSourceProvider
from src.context.models import ContextItem
from src.context.working_context_runtime import WorkingContextRuntime
from src.core.jarvis import JARVIS


class InspectingProvider(AIProvider):
    def __init__(self):
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return AIResponse(
            content="working-context response",
            provider="inspecting",
            model="test-model",
            finish_reason="completed",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "inspecting"


class StaticSourceProvider(ContextSourceProvider):
    def __init__(self):
        self.sources = (
            ContextSource(
                source_id="memory:1",
                source_type="MEMORY",
                relevance_score=0.9,
                priority=100,
            ),
        )

    def get_sources(self, request):
        return self.sources

    def get_context_items(self, request, sources):
        return {
            "memory:1": ContextItem(
                source_type="MEMORY",
                content="Selected persistent context.",
                relevance_score=0.9,
                provenance={"source_id": "memory:1"},
            ),
        }


class JARVISWorkingContextIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.original_database_path = database.DATABASE_PATH
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "test.db"
        database.set_database_path(self.database_path)
        self._create_schema()

        self.provider = InspectingProvider()
        self.ai_service = AIService(default_provider="inspecting")
        self.ai_service.register_provider(self.provider)

    def tearDown(self):
        database.set_database_path(self.original_database_path)
        self.temp_directory.cleanup()

    def _create_schema(self):
        connection = sqlite3.connect(self.database_path)
        connection.executescript(
            """
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at REAL,
                updated_at REAL,
                is_archived INTEGER,
                is_starred INTEGER
            );
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL,
                parent_id TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );
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
            );
            CREATE TABLE memory_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                conversation_id TEXT,
                message_id TEXT,
                evidence_text TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                source_created_at TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.commit()
        connection.close()

    def test_jarvis_conversation_consumes_working_context(self):
        runtime = WorkingContextRuntime(StaticSourceProvider())
        jarvis = JARVIS(
            ai_service=self.ai_service,
            working_context_runtime=runtime,
        )

        response = jarvis.ask("Tell me about the project.")

        self.assertEqual(response.context.items[0].content, "Selected persistent context.")
        self.assertEqual(
            response.metadata["source_selection"],
            ("memory:1",),
        )
        self.assertEqual(len(self.provider.requests), 1)
        request = self.provider.requests[0]
        self.assertTrue(request.metadata["working_context_consumed"])
        self.assertEqual(
            request.context["context"]["items"][0]["content"],
            "Selected persistent context.",
        )
        self.assertEqual(
            request.context["source_selection"]["selected_source_ids"],
            ("memory:1",),
        )

    def test_default_runtime_uses_memory_source_provider(self):
        jarvis = JARVIS(ai_service=self.ai_service)
        self.assertIsInstance(
            jarvis.working_context_runtime.source_provider,
            MemoryContextSourceProvider,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
