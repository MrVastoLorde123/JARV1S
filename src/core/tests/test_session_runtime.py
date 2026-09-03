import unittest

from src.core.models import JARVISResponse
from src.core.session_runtime import SessionRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest
from src.interface.request import InterfaceRequestBridge, JARVISRequest


class FakeProcessor:
    def __init__(self, name):
        self.name = name
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        return JARVISResponse(
            content=f"{self.name}: {query}",
            ai_response=None,
            context=None,
            metadata={"processor": self.name},
        )


class SessionRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.default = FakeProcessor("default")
        self.created = {}

        def factory(session_id):
            processor = FakeProcessor(session_id)
            self.created[session_id] = processor
            return processor

        self.runtime = SessionRuntime(
            default_processor=self.default,
            session_processor_factory=factory,
        )

    def request(self, content, session_id=None):
        return JARVISRequest(
            request_id=f"request-{len(content)}-{session_id}",
            content=content,
            channel=InterfaceChannel.TEXT,
            session_id=session_id,
        )

    def test_request_must_be_jarvis_request(self):
        with self.assertRaises(TypeError):
            self.runtime.process(object())

    def test_no_session_uses_default_processor(self):
        result = self.runtime.process(self.request("hello"))
        self.assertIsNone(result.session_id)
        self.assertEqual(self.default.calls, ["hello"])
        self.assertEqual(result.to_interface_response().content, "default: hello")

    def test_session_creates_one_processor_binding(self):
        first = self.runtime.process(self.request("first", "session-a"))
        second = self.runtime.process(self.request("second", "session-a"))

        self.assertEqual(first.session_id, "session-a")
        self.assertEqual(second.session_id, "session-a")
        self.assertEqual(self.runtime.session_count(), 1)
        self.assertEqual(len(self.created["session-a"].calls), 2)
        self.assertEqual(self.created["session-a"].calls, ["first", "second"])

    def test_different_sessions_are_isolated(self):
        self.runtime.process(self.request("a", "session-a"))
        self.runtime.process(self.request("b", "session-b"))

        self.assertEqual(self.runtime.session_count(), 2)
        self.assertEqual(self.created["session-a"].calls, ["a"])
        self.assertEqual(self.created["session-b"].calls, ["b"])

    def test_session_factory_receives_only_session_identity(self):
        received = []

        def factory(session_id):
            received.append(session_id)
            return FakeProcessor(session_id)

        runtime = SessionRuntime(self.default, factory)
        request = self.request("do not reinterpret me", "session-z")
        runtime.process(request)

        self.assertEqual(received, ["session-z"])

    def test_request_content_remains_the_only_core_query(self):
        request = JARVISRequest(
            request_id="req-1",
            content="actual content",
            channel=InterfaceChannel.API,
            session_id="session-1",
            metadata={"provider": "forbidden", "intent": "ignored"},
        )
        runtime = SessionRuntime(self.default)
        runtime.process(request)

        self.assertEqual(self.default.calls, ["actual content"])

    def test_result_preserves_session_and_request_identity(self):
        request = self.request("hello", "session-7")
        result = self.runtime.process(request)

        self.assertEqual(result.session_id, "session-7")
        self.assertEqual(result.result.request_id, request.request_id)
        self.assertEqual(result.result.session_id, request.session_id)

    def test_projection_stays_non_authoritative(self):
        result = self.runtime.process(self.request("hello", "session-1"))
        response = result.to_interface_response()

        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_clearing_binding_does_not_mutate_processor_history(self):
        self.runtime.process(self.request("first", "session-a"))
        processor = self.created["session-a"]
        self.runtime.clear_session("session-a")

        self.assertEqual(self.runtime.session_count(), 0)
        self.assertEqual(processor.calls, ["first"])

    def test_clear_all_sessions_removes_only_bindings(self):
        self.runtime.process(self.request("a", "session-a"))
        self.runtime.process(self.request("b", "session-b"))
        self.runtime.clear_all_sessions()

        self.assertEqual(self.runtime.session_count(), 0)
        self.assertEqual(self.created["session-a"].calls, ["a"])
        self.assertEqual(self.created["session-b"].calls, ["b"])

    def test_factory_invalid_processor_is_rejected(self):
        runtime = SessionRuntime(
            default_processor=self.default,
            session_processor_factory=lambda _: object(),
        )
        with self.assertRaises(TypeError):
            runtime.process(self.request("hello", "session-x"))

    def test_interface_bridge_flows_into_session_runtime(self):
        interface_request = InterfaceRequest(
            request_id="interface-1",
            channel=InterfaceChannel.TEXT,
            content="hello from interface",
            session_id="session-1",
        )
        jarvis_request = InterfaceRequestBridge().to_jarvis_request(interface_request)
        result = self.runtime.process(jarvis_request)

        response = result.to_interface_response()
        self.assertEqual(response.request_id, interface_request.request_id)
        self.assertEqual(response.session_id, interface_request.session_id)
        self.assertEqual(response.content, "session-1: hello from interface")


if __name__ == "__main__":
    unittest.main(verbosity=2)
