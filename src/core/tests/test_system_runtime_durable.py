import unittest

from src.core.conversation_store import ConversationStore
from src.core.durable_session_runtime import DurableSessionRuntime
from src.core.models import JARVISResponse
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel


class FakeProcessor:
    def __init__(self, label):
        self.label = label
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        return JARVISResponse(
            content=f"{self.label}: {query}",
            ai_response=None,
            context=None,
            metadata={"label": self.label},
        )


class InMemoryConversationStore(ConversationStore):
    def __init__(self):
        self.ids = set()

    def conversation_exists(self, conversation_id):
        return conversation_id in self.ids

    def create_conversation(self, title=None, conversation_id=None):
        conversation_id = conversation_id or "generated"
        self.ids.add(conversation_id)
        return type("Record", (), {"conversation_id": conversation_id})()


class DurableSystemRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryConversationStore()
        self.default = FakeProcessor("default")
        self.created = []

        def factory(session_id, conversation_id):
            processor = FakeProcessor(f"{session_id}/{conversation_id}")
            self.created.append(processor)
            return processor

        self.factory = factory
        self.runtime = SystemRuntime(
            self.default,
            conversation_store=self.store,
            durable_processor_factory=factory,
        )

    def test_system_runtime_uses_durable_session_runtime(self):
        self.assertIsInstance(self.runtime.session_runtime, DurableSessionRuntime)

    def test_receive_creates_and_reuses_persistent_session_identity(self):
        first = self.runtime.receive(
            request_id="r1",
            channel=InterfaceChannel.TEXT,
            content="first",
            session_id="session-a",
        )
        second = self.runtime.receive(
            request_id="r2",
            channel=InterfaceChannel.TEXT,
            content="second",
            session_id="session-a",
        )

        self.assertEqual(first.session_id, "session-a")
        self.assertEqual(second.session_id, "session-a")
        self.assertEqual(self.store.ids, {"session-a"})
        self.assertEqual(len(self.created), 1)
        self.assertEqual(self.created[0].calls, ["first", "second"])

    def test_new_runtime_reuses_existing_persistent_session(self):
        self.runtime.receive(
            request_id="r1",
            channel=InterfaceChannel.TEXT,
            content="before restart",
            session_id="session-a",
        )
        restarted = SystemRuntime(
            self.default,
            conversation_store=self.store,
            durable_processor_factory=self.factory,
        )
        result = restarted.receive(
            request_id="r2",
            channel=InterfaceChannel.TEXT,
            content="after restart",
            session_id="session-a",
        )
        self.assertEqual(result.session_id, "session-a")
        self.assertEqual(self.store.ids, {"session-a"})

    def test_clearing_runtime_binding_does_not_delete_persistent_identity(self):
        self.runtime.receive(
            request_id="r1",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-a",
        )
        self.runtime.session_runtime.clear_session_binding("session-a")
        self.assertIn("session-a", self.store.ids)

    def test_durability_does_not_change_core_query(self):
        self.runtime.receive(
            request_id="r1",
            channel=InterfaceChannel.API,
            content="actual content",
            session_id="session-a",
        )
        self.assertEqual(self.created[0].calls, ["actual content"])

    def test_projection_remains_non_authoritative(self):
        result = self.runtime.receive(
            request_id="r1",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-a",
        )
        response = self.runtime.respond(result)
        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_cannot_supply_both_custom_session_runtime_and_store(self):
        with self.assertRaises(ValueError):
            SystemRuntime(
                self.default,
                session_runtime=self.runtime.session_runtime,
                conversation_store=self.store,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
