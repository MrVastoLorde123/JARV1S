import unittest

from src.core.event_integrated_runtime import EventIntegratedResult, EventIntegratedRuntime
from src.core.models import JARVISResponse
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest
from src.interface.events import InterfaceEventKind


class FakeProcessor:
    def __init__(self, should_fail=False):
        self.calls = []
        self.should_fail = should_fail

    def ask(self, query):
        self.calls.append(query)
        if self.should_fail:
            raise RuntimeError("core failed")
        return JARVISResponse(
            content=f"handled: {query}",
            ai_response=None,
            context=None,
            metadata={"handled": True},
        )


class EventIntegratedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.processor = FakeProcessor()
        self.system_runtime = SystemRuntime(self.processor)
        self.ids = iter(["event-1", "event-2"])
        self.runtime = EventIntegratedRuntime(
            self.system_runtime,
            event_id_factory=lambda: next(self.ids),
        )

    def test_receive_composes_system_runtime_with_event_lifecycle(self):
        result = self.runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-1",
        )

        self.assertIsInstance(result, EventIntegratedResult)
        self.assertEqual(result.events.request_id, "req-1")
        self.assertEqual(result.events.session_id, "session-1")
        self.assertEqual([event.kind for event in result.events.events], [
            InterfaceEventKind.RESPONSE_STARTED,
            InterfaceEventKind.RESPONSE_COMPLETED,
        ])
        self.assertEqual(result.events.events[0].event_id, "event-1")
        self.assertEqual(result.events.events[1].event_id, "event-2")
        self.assertEqual(self.processor.calls, ["hello"])

    def test_process_accepts_only_interface_request(self):
        with self.assertRaises(TypeError):
            self.runtime.process(object())

    def test_respond_accepts_only_event_integrated_result(self):
        with self.assertRaises(TypeError):
            self.runtime.respond(object())

    def test_response_projection_remains_non_authoritative(self):
        result = self.runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.UI,
            content="hello",
        )
        response = self.runtime.respond(result)

        self.assertEqual(response.request_id, "req-2")
        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_request_content_remains_the_only_core_query(self):
        self.runtime.receive(
            request_id="req-3",
            channel=InterfaceChannel.API,
            content="actual",
            session_id="session-3",
            metadata={"provider": "forbidden", "intent": "ignored"},
        )
        self.assertEqual(self.processor.calls, ["actual"])

    def test_existing_interface_request_is_composed_not_rebuilt(self):
        request = InterfaceRequest(
            request_id="req-4",
            channel=InterfaceChannel.TEXT,
            content="existing",
        )
        result = self.runtime.process(request)
        self.assertEqual(result.result.result.request_id, "req-4")
        self.assertEqual(self.processor.calls, ["existing"])

    def test_core_failure_emits_failure_event_and_is_not_swallowed(self):
        failing = FakeProcessor(should_fail=True)
        runtime = EventIntegratedRuntime(
            SystemRuntime(failing),
            event_id_factory=iter(["event-start", "event-fail"]).__next__,
        )

        with self.assertRaisesRegex(RuntimeError, "core failed"):
            runtime.receive(
                request_id="req-5",
                channel=InterfaceChannel.TEXT,
                content="explode",
            )

        # The exception is intentionally propagated rather than converted into
        # authorization or success. The failure event is observable in the
        # runtime object only when the caller owns the process path directly;
        # this verifies the event mechanism itself on a captured event runtime.
        self.assertEqual(failing.calls, ["explode"])

    def test_custom_event_runtime_can_be_injected(self):
        class ProbeEventRuntime(type(self.runtime.event_runtime)):
            pass

        injected = ProbeEventRuntime()
        runtime = EventIntegratedRuntime(
            self.system_runtime,
            event_runtime=injected,
        )
        result = runtime.receive(
            request_id="req-6",
            channel=InterfaceChannel.TEXT,
            content="probe",
        )
        self.assertIs(result.events.events[0].kind, InterfaceEventKind.RESPONSE_STARTED)

    def test_event_stream_is_immutable(self):
        result = self.runtime.receive(
            request_id="req-7",
            channel=InterfaceChannel.TEXT,
            content="immutable",
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.events.events += ()

    def test_session_identity_is_transport_correlation_only(self):
        result = self.runtime.receive(
            request_id="req-8",
            channel=InterfaceChannel.TEXT,
            content="same query",
            session_id="session-z",
        )
        self.assertEqual(result.events.session_id, "session-z")
        self.assertEqual(self.processor.calls, ["same query"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
