import unittest

from src.core.jarvis_runtime import JARVISRuntime
from src.core.models import JARVISResponse
from src.core.recovery_integrated_runtime import RecoveryIntegratedResult
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest
from src.interface.events import InterfaceEventKind
from src.interface.reliability import InterfaceRecoveryAction, InterfaceReliabilityState


class FakeProcessor:
    def __init__(self):
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        return JARVISResponse(
            content=f"handled: {query}",
            ai_response=None,
            context=None,
            metadata={"handled": True, "route": "TASK", "stage": "EXECUTION"},
        )


class FailingProcessor:
    def ask(self, query):
        raise RuntimeError("processor failure")


class JARVISRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.processor = FakeProcessor()

    def test_constructor_accepts_only_canonical_recovery_runtime(self):
        from src.core.event_integrated_runtime import EventIntegratedRuntime
        from src.core.recovery_integrated_runtime import RecoveryIntegratedRuntime

        integrated = EventIntegratedRuntime(SystemRuntime(self.processor))
        recovery = RecoveryIntegratedRuntime(integrated)
        runtime = JARVISRuntime(recovery)

        self.assertIs(runtime.recovery_runtime, recovery)
        self.assertIs(runtime.event_integrated_runtime, integrated)
        self.assertIs(runtime.system_runtime, integrated.system_runtime)

    def test_constructor_rejects_non_runtime(self):
        with self.assertRaises(TypeError):
            JARVISRuntime(object())

    def test_from_processor_builds_one_canonical_composition(self):
        runtime = JARVISRuntime.from_processor(
            self.processor,
            event_id_factory=iter(["event-1", "event-2"]).__next__,
            recovery_id_factory=iter(["recovery-1"]).__next__,
        )

        result = runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="hello",
        )

        self.assertIsInstance(result, RecoveryIntegratedResult)
        self.assertEqual(self.processor.calls, ["hello"])
        self.assertEqual(
            [event.kind for event in result.result.events.events],
            [InterfaceEventKind.RESPONSE_STARTED, InterfaceEventKind.RESPONSE_COMPLETED],
        )
        self.assertEqual(result.recovery.state, InterfaceReliabilityState.HEALTHY)
        self.assertEqual(result.recovery.recovery_action, InterfaceRecoveryAction.NONE)

    def test_receive_delegates_without_reinterpreting_metadata(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.API,
            content="actual",
            session_id="session-2",
            metadata={"provider": "forbidden", "intent": "ignored"},
        )

        self.assertEqual(self.processor.calls, ["actual"])

    def test_process_accepts_only_interface_request(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        with self.assertRaises(TypeError):
            runtime.process(object())

        request = InterfaceRequest(
            request_id="req-3",
            channel=InterfaceChannel.TEXT,
            content="existing",
        )
        result = runtime.process(request)
        self.assertEqual(self.processor.calls, ["existing"])
        self.assertEqual(result.recovery.request_id, "req-3")

    def test_respond_accepts_only_recovery_integrated_result(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        with self.assertRaises(TypeError):
            runtime.respond(object())

    def test_live_control_plane_projects_operation_state(self):
        runtime = JARVISRuntime.from_processor(
            self.processor,
            event_id_factory=iter(["event-1", "event-2"]).__next__,
        )

        result = runtime.receive(
            request_id="req-control",
            channel=InterfaceChannel.TEXT,
            content="do the task",
            session_id="session-control",
        )

        operation = runtime.control_plane.current_operation("req-control")
        self.assertIsNotNone(operation)
        self.assertEqual(operation.request_id, "req-control")
        self.assertEqual(operation.stage, "EXECUTION")
        self.assertEqual(operation.metadata["route"], "TASK")
        self.assertEqual(runtime.control_plane.activity_stream.size, 2)

        state = runtime.control_plane.session_state("session-control")
        self.assertIsNotNone(state)
        self.assertEqual(state.event_count, 2)
        self.assertEqual(state.latest_request_id, "req-control")
        self.assertEqual(state.latest_stage, "EXECUTION")

        self.assertIsInstance(result, RecoveryIntegratedResult)

    def test_control_plane_observes_runtime_failure_without_swallowing_it(self):
        runtime = JARVISRuntime.from_processor(FailingProcessor())

        with self.assertRaisesRegex(RuntimeError, "processor failure"):
            runtime.receive(
                request_id="req-failure",
                channel=InterfaceChannel.TEXT,
                content="fail",
                session_id="session-failure",
            )

        operation = runtime.control_plane.current_operation("req-failure")
        self.assertIsNotNone(operation)
        self.assertEqual(operation.stage, "RUNTIME")
        self.assertEqual(operation.kind.value, "REQUEST_FAILED")
        self.assertEqual(operation.metadata["error_type"], "RuntimeError")

    def test_control_plane_has_no_authority_or_persistence_powers(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        control_plane = runtime.control_plane

        for name in (
            "authorizes_execution",
            "executes_capability",
            "mutates_runtime_state",
            "persists_state",
            "establishes_truth",
            "establishes_certainty",
        ):
            self.assertFalse(getattr(control_plane, name))

    def test_response_projection_remains_non_authoritative(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        result = runtime.receive(
            request_id="req-4",
            channel=InterfaceChannel.UI,
            content="hello",
        )
        response = runtime.respond(result)

        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_subsystems_are_composed_not_duplicated(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        self.assertIs(runtime.system_runtime, runtime.event_integrated_runtime.system_runtime)
        self.assertIs(
            runtime.event_integrated_runtime,
            runtime.recovery_runtime.event_integrated_runtime,
        )

    def test_recovery_state_remains_bounded_and_non_authoritative(self):
        runtime = JARVISRuntime.from_processor(
            self.processor,
            recovery_id_factory=iter(["recovery-5"]).__next__,
        )
        result = runtime.receive(
            request_id="req-5",
            channel=InterfaceChannel.TEXT,
            content="state",
        )

        self.assertEqual(len(result.recovery.records), 1)
        payload = result.recovery.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_optional_durable_session_composition_passes_through(self):
        from src.core.conversation_store import ConversationStore

        runtime = JARVISRuntime.from_processor(
            self.processor,
            conversation_store=ConversationStore(),
        )
        self.assertIsNotNone(runtime.system_runtime.session_runtime)

    def test_interface_request_identity_is_transport_correlation_only(self):
        runtime = JARVISRuntime.from_processor(self.processor)
        request = InterfaceRequest(
            request_id="req-6",
            channel=InterfaceChannel.VOICE,
            content="same query",
            session_id="session-6",
        )
        result = runtime.process(request)

        self.assertEqual(result.recovery.request_id, "req-6")
        self.assertEqual(result.result.result.result.session_id, "session-6")
        self.assertEqual(self.processor.calls, ["same query"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
