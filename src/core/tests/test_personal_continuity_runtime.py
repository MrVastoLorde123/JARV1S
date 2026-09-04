import tempfile
import unittest
from pathlib import Path

from src import database
from src.core.jarvis import JARVIS
from src.core.jarvis_runtime import JARVISRuntime
from src.core.conversation_store import ConversationStore
from src.core.models import JARVISResponse
from src.database_bootstrap import bootstrap_database


class FakeAIResponse:
    provider = "fake"
    model = "continuity-test"

    def __init__(self, content):
        self.content = content


class FakeAIService:
    def __init__(self):
        self.requests = []

    def generate(self, request, provider_name=None):
        del provider_name
        self.requests.append(request)
        state_items = [
            item["content"]
            for item in request.context["context"]["items"]
            if item["source_type"] == "STATE"
        ]
        if state_items:
            content = "Remembered context: " + " | ".join(state_items)
        else:
            content = "No prior context."
        return FakeAIResponse(content)


class PersonalContinuityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.original_database_path = database.DATABASE_PATH
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "continuity.db"
        database.set_database_path(self.database_path)
        bootstrap_database()

    def tearDown(self):
        database.set_database_path(self.original_database_path)
        self.temp_directory.cleanup()

    def test_conversation_survives_runtime_restart(self):
        ai_service = FakeAIService()
        store = ConversationStore()
        session_id = "continuity-session"

        def processor_factory(session, conversation_id):
            self.assertEqual(session, session_id)
            return JARVIS(
                ai_service=ai_service,
                conversation_store=store,
                conversation_id=conversation_id,
                enable_memory_formation=False,
            )

        first_runtime = JARVISRuntime.from_processor(
            JARVIS(ai_service=ai_service),
            conversation_store=store,
            durable_processor_factory=processor_factory,
        )
        first = first_runtime.receive(
            request_id="request-1",
            channel=self._channel(),
            content="My current project is JARVIS.",
            session_id=session_id,
        )
        first_response = first.to_interface_response()
        self.assertEqual(first_response.request_id, "request-1")
        self.assertIn("No prior context.", first_response.content)

        second_runtime = JARVISRuntime.from_processor(
            JARVIS(ai_service=ai_service),
            conversation_store=store,
            durable_processor_factory=processor_factory,
        )
        second = second_runtime.receive(
            request_id="request-2",
            channel=self._channel(),
            content="What were we discussing?",
            session_id=session_id,
        )

        response = second.to_interface_response()
        self.assertIn("user: My current project is JARVIS.", response.content)
        self.assertIn("assistant: No prior context.", response.content)
        self.assertEqual(store.get_messages(session_id)[0][3], "My current project is JARVIS.")
        self.assertEqual(len(store.get_messages(session_id)), 4)

    def test_new_session_does_not_inherit_previous_conversation(self):
        ai_service = FakeAIService()
        store = ConversationStore()

        def processor_factory(session_id, conversation_id):
            return JARVIS(
                ai_service=ai_service,
                conversation_store=store,
                conversation_id=conversation_id,
                enable_memory_formation=False,
            )

        runtime = JARVISRuntime.from_processor(
            JARVIS(ai_service=ai_service),
            conversation_store=store,
            durable_processor_factory=processor_factory,
        )
        runtime.receive(
            request_id="request-a",
            channel=self._channel(),
            content="Remember only this session.",
            session_id="session-a",
        )
        result = runtime.receive(
            request_id="request-b",
            channel=self._channel(),
            content="What do you know from before?",
            session_id="session-b",
        )

        response = result.to_interface_response()
        self.assertNotIn("Remember only this session.", response.content)

    @staticmethod
    def _channel():
        from src.interface.boundary import InterfaceChannel

        return InterfaceChannel.TEXT


if __name__ == "__main__":
    unittest.main(verbosity=2)
