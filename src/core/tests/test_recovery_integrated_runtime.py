import unittest

from src.core.event_integrated_runtime import EventIntegratedRuntime
from src.core.models import JARVISResponse
from src.core.recovery_integrated_runtime import RecoveryIntegratedResult, RecoveryIntegratedRuntime
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest
from src.interface.events import InterfaceEventKind
from src.interface.reliability import (
    InterfaceRecoveryAction,
    InterfaceReliabilityRuntime,
    InterfaceReliabilityState,
)


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


class CapturingReliabilityRuntime(InterfaceReliabilityRuntime):
    def __init__(self):
        self.started = None
        self.healthy_state = None
        self.failed_state = None

    def start(self, request_id, *, max_records=32):
        self.started = super().start(request_id, max_records=max_records)
        return self.started

    def healthy(self, state, *, record_id, metadata=None):
        self.healthy_state = super().healthy(
            state,
            record_id=record_id,
            metadata=metadata,
        )
        return self.healthy_state

    def failed(self, state, *, record_id, reason, action=InterfaceRecoveryAction.ABANDON, attempt=0, metadata=None):
        self.failed_state = super().failed(
            state,
            record_id=record_id,
            reason=reason,
            action=action,
            attempt=attempt,
            metadata=metadata,
        )
        return self.failed_state


class RecoveryIntegratedRuntimeTests(unittest.TestCase):
    def setUp(self):
        processor = FakeProcessor()
        event_runtime = EventIntegratedRuntime(
            SystemRuntime(processor),
            event_id_factory=iter(["event-1", "event-2"]).__next__,
        )
        self.processor = processor
        self.runtime = RecoveryIntegratedRuntime(
            event_runtime,
            recovery_id_factory=iter(["recovery-1"]).__next__,
        )

    def test_receive_composes_event_runtime_with_healthy_recovery_state(self):
        result = self.runtime.receive(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-1",
        )

        self.assertIsInstance(result, RecoveryIntegratedResult)
        self.assertEqual(result.recovery.request_id, "req-1")
        self.assertEqual(result.recovery.state, InterfaceReliabilityState.HEALTHY)
        self.assertEqual(result.recovery.recovery_action, InterfaceRecoveryAction.NONE)
        self.assertEqual(result.recovery.latest.record_id, "recovery-1")
        self.assertEqual(
            [event.kind for event in result.result.events.events],
            [InterfaceEventKind.RESPONSE_STARTED, InterfaceEventKind.RESPONSE_COMPLETED],
        )
        self.assertEqual(self.processor.calls, ["hello"])

    def test_process_accepts_only_interface_request(self):
        with self.assertRaises(TypeError):
            self.runtime.process(object())

    def test_respond_accepts_only_recovery_integrated_result(self):
        with self.assertRaises(TypeError):
            self.runtime.respond(object())

    def test_response_projection_remains_non_authoritative(self):
        result = self.runtime.receive(
            request_id="req-2",
            channel=InterfaceChannel.UI,
            content="hello",
        )
        response = self.runtime.respond(result)

        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["authorization_granted"])
        self.assertFalse(response.metadata["execution_requested"])

    def test_failure_is_re_raised_and_recorded_as_abandon(self):
        failing = FakeProcessor(should_fail=True)
        reliability = CapturingReliabilityRuntime()
        event_runtime = EventIntegratedRuntime(
            SystemRuntime(failing),
            event_id_factory=iter(["event-start", "event-fail"]).__next__,
        )
        runtime = RecoveryIntegratedRuntime(
            event_runtime,
            reliability_runtime=reliability,
            recovery_id_factory=iter(["recovery-fail"]).__next__,
        )

        with self.assertRaisesRegex(RuntimeError, "core failed"):
            runtime.receive(
                request_id="req-3",
                channel=InterfaceChannel.TEXT,
                content="explode",
            )

        self.assertEqual(reliability.failed_state.state, InterfaceReliabilityState.FAILED)
        self.assertEqual(reliability.failed_state.recovery_action, InterfaceRecoveryAction.ABANDON)
        self.assertIn("core failed", reliability.failed_state.latest.reason)
        self.assertEqual(failing.calls, ["explode"])

    def test_recovery_action_is_mechanical_only(self):
        state = self.runtime.reliability_runtime.start("req-4")
        state = self.runtime.reliability_runtime.degrade(
            state,
            record_id="degrade-1",
            reason="transport degraded",
            action=InterfaceRecoveryAction.RETRY,
        )
        state = self.runtime.reliability_runtime.recover(
            state,
            record_id="recover-1",
            action=InterfaceRecoveryAction.RESUME,
        )

        self.assertEqual(state.state, InterfaceReliabilityState.RECOVERING)
        self.assertEqual(state.recovery_action, InterfaceRecoveryAction.RESUME)
        self.assertFalse(state.latest.to_dict()["authorization_granted"])
        self.assertFalse(state.latest.to_dict()["execution_requested"])

    def test_request_content_and_session_identity_are_not_reinterpreted(self):
        request = InterfaceRequest(
            request_id="req-5",
            channel=InterfaceChannel.API,
            content="actual query",
            session_id="session-5",
            metadata={"provider": "forbidden", "retry": True},
        )
        result = self.runtime.process(request)

        self.assertEqual(self.processor.calls, ["actual query"])
        self.assertEqual(result.recovery.request_id, "req-5")
        self.assertEqual(result.result.result.result.session_id, "session-5")

    def test_result_and_recovery_state_are_immutable(self):
        result = self.runtime.receive(
            request_id="req-6",
            channel=InterfaceChannel.TEXT,
            content="immutable",
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.recovery.records += ()
        with self.assertRaises((AttributeError, TypeError)):
            result.result = result.result

    def test_custom_reliability_runtime_can_be_injected(self):
        reliability = CapturingReliabilityRuntime()
        runtime = RecoveryIntegratedRuntime(
            self.runtime.event_integrated_runtime,
            reliability_runtime=reliability,
            recovery_id_factory=lambda: "custom-recovery",
        )
        result = runtime.receive(
            request_id="req-7",
            channel=InterfaceChannel.TEXT,
            content="probe",
        )

        self.assertIs(reliability.healthy_state, result.recovery)
        self.assertEqual(reliability.healthy_state.latest.record_id, "custom-recovery")

    def test_missing_integrated_runtime_is_rejected(self):
        with self.assertRaises(TypeError):
            RecoveryIntegratedRuntime(object())

    def test_recovery_serialization_is_non_authoritative(self):
        result = self.runtime.receive(
            request_id="req-8",
            channel=InterfaceChannel.TEXT,
            content="serialize",
        )
        payload = result.recovery.to_dict()

        self.assertEqual(payload["state"], "HEALTHY")
        self.assertEqual(payload["recovery_action"], "NONE")
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
