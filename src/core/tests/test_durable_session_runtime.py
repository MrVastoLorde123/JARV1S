import unittest

from src.core.conversation_store import ConversationStore
from src.core.models import JARVISResponse
from src.core.durable_session_runtime import DurableSessionRuntime
from src.interface.boundary import InterfaceChannel
from src.interface.request import JARVISRequest


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


class DurableSessionRuntimeTests(unittest.TestCase):
    def setUp(self):
        class InMemoryStore(ConversationStore):
            def __init__(self):
                self.records = set()
                self.created = []

            def conversation_exists(self, conversation_id):
                return conversation_id in self.records

            def create_conversation(self, conversation_id=None, title=None):
                cid = conversation_id or "generated"
                self.records.add(cid)
                self.created.append(cid)
                return type("Record", (), {"conversation_id": cid})()

        self.store = InMemoryStore()
        self.created_processors = []

        def factory(session_id, conversation_id):
            processor = FakeProcessor(f"{session_id}/{conversation_id}")
            self.created_processors.append(processor)
            return processor

        self.default = FakeProcessor("default")
        self.runtime = DurableSessionRuntime(self.default, self.store, factory)
        self.factory = factory

    def request(self, content, session_id):
        return JARVISRequest(
            request_id=f"req-{content}",
            content=content,
            channel=InterfaceChannel.TEXT,
            session_id=session_id,
        )

    def test_first_session_creates_persistent_conversation_identity(self):
        self.runtime.process(self.request("hello", "session-a"))
        self.assertEqual(self.store.created, ["session-a"])
        self.assertEqual(self.runtime.session_record("session-a").conversation_id, "session-a")

    def test_existing_conversation_is_reused_after_runtime_restart(self):
        first = DurableSessionRuntime(self.default, self.store, self.factory)
        first.process(self.request("first", "session-a"))
        calls_before = list(self.created_processors[-1].calls)

        second = DurableSessionRuntime(self.default, self.store, self.factory)
        second.process(self.request("second", "session-a"))

        self.assertEqual(self.store.created, ["session-a"])
        self.assertEqual(second.session_record("session-a").conversation_id, "session-a")
        self.assertEqual(calls_before, ["first"])
        self.assertEqual(self.created_processors[-1].calls, ["second"])

    def test_session_identity_does_not_enter_semantic_query(self):
        self.runtime.process(self.request("actual", "secret-session"))
        self.assertEqual(self.created_processors[-1].calls, ["actual"])

    def test_different_sessions_get_distinct_persistent_records(self):
        self.runtime.process(self.request("a", "session-a"))
        self.runtime.process(self.request("b", "session-b"))
        self.assertEqual(self.store.created, ["session-a", "session-b"])
        self.assertNotEqual(
            self.runtime.session_record("session-a").conversation_id,
            self.runtime.session_record("session-b").conversation_id,
        )

    def test_clearing_runtime_binding_does_not_delete_persistent_conversation(self):
        self.runtime.process(self.request("hello", "session-a"))
        self.runtime.clear_session_binding("session-a")
        self.assertTrue(self.store.conversation_exists("session-a"))
        self.assertIsNone(self.runtime.session_record("session-a"))

    def test_existing_processor_remains_default_without_factory(self):
        runtime = DurableSessionRuntime(self.default, self.store)
        result = runtime.process(self.request("hello", "session-a"))
        self.assertEqual(self.default.calls, ["hello"])
        self.assertEqual(result.session_id, "session-a")

    def test_request_type_is_enforced(self):
        with self.assertRaises(TypeError):
            self.runtime.process(object())

    def test_session_id_must_be_non_empty_for_lifecycle_operations(self):
        with self.assertRaises(ValueError):
            self.runtime.session_record("   ")
        with self.assertRaises(ValueError):
            self.runtime.clear_session_binding("")

    def test_factory_receives_only_session_and_conversation_identity(self):
        received = []

        def factory(session_id, conversation_id):
            received.append((session_id, conversation_id))
            return FakeProcessor("probe")

        runtime = DurableSessionRuntime(self.default, self.store, factory)
        runtime.process(self.request("content", "session-z"))
        self.assertEqual(received, [("session-z", "session-z")])

    def test_result_projection_remains_non_authoritative(self):
        result = self.runtime.process(self.request("hello", "session-a"))
        response = result.to_interface_response()
        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
