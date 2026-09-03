import unittest

from src.core.jarvis import JARVIS
from src.core.models import JARVISResponse
from src.core.session_runtime import SessionRuntimeResult
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest


class FakeProcessor:
    def __init__(self):
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        return JARVISResponse(
            content=f"handled: {query}",
            ai_response=None,
            context=None,
            metadata={"handled": True},
        )


class SystemRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.processor = FakeProcessor()
        self.runtime = SystemRuntime(self.processor)

    def test_receive_constructs_and_routes_canonical_path(self):
        result = self.runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-1",
        )

        self.assertIsInstance(result, SessionRuntimeResult)
        response = self.runtime.respond(result)
        self.assertEqual(response.request_id, "req-1")
        self.assertEqual(response.content, "handled: hello")
        self.assertEqual(response.metadata["session_id"], "session-1")

    def test_process_accepts_only_interface_request(self):
        with self.assertRaises(TypeError):
            self.runtime.process(object())

    def test_respond_accepts_only_session_runtime_result(self):
        with self.assertRaises(TypeError):
            self.runtime.respond(object())

    def test_request_content_is_the_only_core_query(self):
        self.runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.API,
            content="actual content",
            metadata={"provider": "forbidden", "intent": "ignored"},
        )
        self.assertEqual(self.processor.calls, ["actual content"])

    def test_session_identity_is_not_semantic_input(self):
        first = self.runtime.receive(
            request_id="req-3",
            channel=InterfaceChannel.TEXT,
            content="first",
            session_id="session-a",
        )
        second = self.runtime.receive(
            request_id="req-4",
            channel=InterfaceChannel.TEXT,
            content="second",
            session_id="session-a",
        )

        self.assertEqual(first.session_id, "session-a")
        self.assertEqual(second.session_id, "session-a")
        self.assertEqual(self.processor.calls, ["first", "second"])
        self.assertEqual(self.runtime.session_runtime.session_count(), 1)

    def test_different_sessions_remain_isolated_at_runtime_boundary(self):
        self.runtime.receive(
            request_id="req-a",
            channel=InterfaceChannel.TEXT,
            content="a",
            session_id="session-a",
        )
        self.runtime.receive(
            request_id="req-b",
            channel=InterfaceChannel.TEXT,
            content="b",
            session_id="session-b",
        )

        self.assertEqual(self.runtime.session_runtime.session_count(), 2)

    def test_projection_remains_non_authoritative(self):
        result = self.runtime.receive(
            request_id="req-5",
            channel=InterfaceChannel.UI,
            content="hello",
        )
        response = self.runtime.respond(result)

        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_existing_processor_is_composed_not_reimplemented(self):
        injected = FakeProcessor()
        runtime = SystemRuntime(injected)
        runtime.receive(
            request_id="req-6",
            channel=InterfaceChannel.TEXT,
            content="through existing processor",
        )
        self.assertEqual(injected.calls, ["through existing processor"])

    def test_custom_boundaries_can_be_injected(self):
        class BoundaryProbe:
            def __init__(self):
                self.calls = []

            def request(self, **kwargs):
                self.calls.append(kwargs)
                return InterfaceRequest(**kwargs)

        boundary = BoundaryProbe()
        runtime = SystemRuntime(self.processor, interface_boundary=boundary)
        runtime.receive(
            request_id="req-7",
            channel=InterfaceChannel.TEXT,
            content="probe",
        )
        self.assertEqual(boundary.calls[0]["content"], "probe")

    def test_real_jarvis_satisfies_processor_contract(self):
        class MinimalAIService:
            pass

        # Constructor-level contract only; no model/network call is performed.
        jarvis = JARVIS.__new__(JARVIS)
        runtime = SystemRuntime(jarvis)
        self.assertIsNotNone(runtime)

    def test_no_new_authorization_state_is_created(self):
        result = self.runtime.receive(
            request_id="req-8",
            channel=InterfaceChannel.TEXT,
            content="hello",
        )
        response = self.runtime.respond(result)
        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
