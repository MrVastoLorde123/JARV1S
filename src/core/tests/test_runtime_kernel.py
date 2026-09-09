"""Focused M26.1 tests for the JARVIS runtime kernel."""
from __future__ import annotations

from io import StringIO
import unittest

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
)
from src.core.runtime_kernel import JarvisRuntime


class _Orchestration:
    def __init__(self) -> None:
        self.requests: list[InterfaceRequest] = []

    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        self.requests.append(request)
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"result": {"operation": request.operation.value}},
            metadata={"artifact_type": "TEST_STAGE"},
        )


class M26_1JarvisRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestration = _Orchestration()
        self.runtime = JarvisRuntime(
            orchestration=self.orchestration,
            session_id="session-runtime-1",
            actor_id="actor-runtime-1",
        )

    def test_runtime_composes_the_complete_m25_stack(self) -> None:
        self.assertEqual(self.runtime.session_id, "session-runtime-1")
        self.assertEqual(self.runtime.actor_id, "actor-runtime-1")
        self.assertIsNotNone(self.runtime.activity_stream)
        self.assertIsNotNone(self.runtime.session_projector)
        self.assertIsNotNone(self.runtime.interface_adapter)
        self.assertIsNotNone(self.runtime.interface_backend)

    def test_submit_crosses_orchestration_and_records_activity(self) -> None:
        response = self.runtime.submit(
            InterfaceOperation.PROPOSE,
            payload={"value": "test"},
        )
        self.assertEqual(response["status"], "ACCEPTED")
        self.assertEqual(len(self.orchestration.requests), 1)
        request = self.orchestration.requests[0]
        self.assertEqual(request.operation, InterfaceOperation.PROPOSE)
        self.assertEqual(request.session_id, "session-runtime-1")
        events = self.runtime.activity_stream.snapshot()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].request_id, request.request_id)
        self.assertEqual(events[1].stage, "TEST_STAGE")

    def test_status_and_activity_are_session_derived(self) -> None:
        self.assertIn("NO ACTIVITY", self.runtime.render_status())
        self.runtime.submit(InterfaceOperation.PROPOSE)
        status = self.runtime.render_status()
        activity = self.runtime.render_activity()
        self.assertIn("EVENTS 2", status)
        self.assertIn("PROPOSE", status)
        self.assertIn("#1 REQUEST_RECEIVED", activity)
        self.assertIn("#2 RESPONSE_EMITTED", activity)

    def test_handle_line_uses_the_same_composed_runtime(self) -> None:
        result = self.runtime.handle_line('submit PROPOSE {"value":"x"}')
        self.assertIn('"status": "ACCEPTED"', result)
        self.assertEqual(len(self.orchestration.requests), 1)

    def test_run_uses_the_real_terminal_surface(self) -> None:
        input_stream = StringIO("status\nsubmit PROPOSE {}\nactivity\nquit\n")
        output_stream = StringIO()
        self.runtime.run(input_stream, output_stream)
        output = output_stream.getvalue()
        self.assertIn("JARVIS> READY", output)
        self.assertIn("NO ACTIVITY", output)
        self.assertIn("ACCEPTED", output)
        self.assertIn("REQUEST_RECEIVED", output)
        self.assertIn("BYE", output)

    def test_runtime_rejects_invalid_session_identity(self) -> None:
        with self.assertRaises(ValueError):
            JarvisRuntime(
                orchestration=self.orchestration,
                session_id="",
                actor_id="actor-runtime-1",
            )

    def test_runtime_rejects_invalid_orchestration(self) -> None:
        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=object(),
                session_id="session-runtime-1",
                actor_id="actor-runtime-1",
            )

    def test_runtime_has_no_authority_or_execution_powers(self) -> None:
        self.assertFalse(self.runtime.authorizes_execution)
        self.assertFalse(self.runtime.executes_capability)
        self.assertFalse(self.runtime.mutates_state)
        self.assertFalse(self.runtime.persists_state)
        self.assertFalse(self.runtime.establishes_truth)
        self.assertFalse(self.runtime.establishes_certainty)
        self.assertFalse(self.runtime.is_ai_provider)


if __name__ == "__main__":
    unittest.main()
