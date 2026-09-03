import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database
from src.ai.models import AIResponse, AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.context.models import ContextOptions
from src.core.conversation_store import ConversationStore
from src.core.jarvis import JARVIS
from src.core.jarvis_runtime import JARVISRuntime
from src.interface.boundary import InterfaceChannel
from src.interface.events import InterfaceEventKind
from src.interface.reliability import InterfaceRecoveryAction, InterfaceReliabilityState


class FakeAIProvider(AIProvider):
    def generate(self, request):
        return AIResponse(
            content=f"handled: {request.task}",
            provider="fake",
            model="fake-model",
            finish_reason="completed",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "fake"


def create_schema(path):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
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
            ON DELETE CASCADE
        );
        """
    )
    connection.commit()
    connection.close()


class EndToEndRuntimeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.original_database_path = database.DATABASE_PATH
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "integration.db"
        database.set_database_path(self.database_path)
        create_schema(self.database_path)

        self.ai_service = AIService(default_provider="fake")
        self.ai_service.register_provider(FakeAIProvider())
        self.store = ConversationStore()

        def factory(session_id, conversation_id):
            return JARVIS(
                ai_service=self.ai_service,
                conversation_store=self.store,
                conversation_id=conversation_id,
                context_options=ContextOptions(
                    include_memories=False,
                    include_evidence=False,
                    include_history=False,
                    include_state=True,
                ),
            )

        self.factory = factory

    def tearDown(self):
        database.set_database_path(self.original_database_path)
        self.temp_directory.cleanup()

    def build_runtime(self):
        return JARVISRuntime.from_processor(
            JARVIS(ai_service=self.ai_service),
            conversation_store=self.store,
            durable_processor_factory=self.factory,
            event_id_factory=iter(["event-1", "event-2", "event-3", "event-4"]).__next__,
            recovery_id_factory=iter(["recovery-1", "recovery-2"]).__next__,
        )

    def test_real_jarvis_crosses_full_runtime_stack(self):
        runtime = self.build_runtime()
        result = runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="Remember this integration path.",
            session_id="session-1",
        )
        response = runtime.respond(result)

        self.assertEqual(response.request_id, "req-1")
        self.assertEqual(response.content, "handled: Remember this integration path.")
        self.assertEqual(
            [event.kind for event in result.result.events.events],
            [InterfaceEventKind.RESPONSE_STARTED, InterfaceEventKind.RESPONSE_COMPLETED],
        )
        self.assertEqual(result.recovery.state, InterfaceReliabilityState.HEALTHY)
        self.assertEqual(result.recovery.recovery_action, InterfaceRecoveryAction.NONE)

    def test_same_durable_session_reuses_persistent_conversation(self):
        runtime = self.build_runtime()
        runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="first turn",
            session_id="session-1",
        )
        runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="second turn",
            session_id="session-1",
        )

        state = self.store.load_state("session-1")
        turns = state.get_recent_turns()

        self.assertEqual(len(turns), 4)
        self.assertEqual(turns[0].content, "first turn")
        self.assertEqual(turns[2].content, "second turn")

    def test_durable_session_survives_runtime_restart(self):
        first_runtime = self.build_runtime()
        first_runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="before restart",
            session_id="session-1",
        )

        second_runtime = self.build_runtime()
        result = second_runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="after restart",
            session_id="session-1",
        )

        self.assertEqual(result.recovery.state, InterfaceReliabilityState.HEALTHY)
        state = self.store.load_state("session-1")
        contents = [turn.content for turn in state.get_recent_turns()]
        self.assertEqual(
            contents,
            [
                "before restart",
                "handled: before restart",
                "after restart",
                "handled: after restart",
            ],
        )

    def test_session_identity_does_not_change_semantic_content(self):
        runtime = self.build_runtime()
        result = runtime.receive(
            request_id="req-3",
            channel=InterfaceChannel.API,
            content="semantic payload",
            session_id="secret-session",
        )

        self.assertEqual(
            result.result.result.result.core_response.content,
            "handled: semantic payload",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
