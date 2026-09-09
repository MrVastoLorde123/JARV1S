import io
import unittest
from types import MappingProxyType

from src.core.interface_adapter import InterfaceAdapter
from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceResponse,
    InterfaceResponseStatus,
    SelfImprovementInterfaceBackend,
)
from src.core.interface_session_state import InterfaceSessionStateProjector
from src.core.runtime_activity_stream import (
    InterfaceRuntimeActivityRecorder,
    ObservableInterfaceOrchestration,
    RuntimeActivityStream,
)
from src.interface_surface import TerminalInterfaceError, TerminalInterfaceSurface


class _Orchestration:
    def __init__(self):
        self.requests = []

    def dispatch(self, request):
        self.requests.append(request)
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"result": {"operation": request.operation.value}},
            metadata={"artifact_type": "TEST_STAGE"},
        )


class M25_6TerminalInterfaceSurfaceTests(unittest.TestCase):
    def _surface(self, *, session_id="session-256", actor_id="actor-256"):
        orchestration = _Orchestration()
        stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(stream)
        observable = ObservableInterfaceOrchestration(orchestration, recorder)
        backend = SelfImprovementInterfaceBackend(observable)
        adapter = InterfaceAdapter(backend)
        projector = InterfaceSessionStateProjector()
        return TerminalInterfaceSurface(
            adapter=adapter,
            activity_stream=stream,
            session_projector=projector,
            session_id=session_id,
            actor_id=actor_id,
        ), orchestration, stream, projector

    def test_surface_requires_exact_dependencies(self):
        surface_data = self._surface()
        with self.assertRaises(TypeError):
            TerminalInterfaceSurface(
                adapter=object(),
                activity_stream=surface_data[2],
                session_projector=surface_data[3],
                session_id="s",
                actor_id="a",
            )

    def test_initial_status_is_no_activity(self):
        surface, _, _, _ = self._surface()
        self.assertEqual(surface.render_status(), "SESSION session-256 | NO ACTIVITY")

    def test_help_is_human_readable(self):
        surface, _, _, _ = self._surface()
        self.assertIn("submit <OPERATION> [JSON]", surface.handle_line("help"))

    def test_submit_translates_and_preserves_backend_contract(self):
        surface, orchestration, _, projector = self._surface()
        response = surface.submit(
            "PROPOSE",
            payload={"value": 1},
            metadata={"source": "terminal"},
        )
        self.assertEqual(response["operation"], "PROPOSE")
        self.assertEqual(response["status"], "ACCEPTED")
        self.assertEqual(orchestration.requests[0].request_id, "terminal-request-1")
        self.assertEqual(orchestration.requests[0].session_id, "session-256")
        self.assertIs(orchestration.requests[0].operation, InterfaceOperation.PROPOSE)
        self.assertEqual(projector.state("session-256").event_count, 2)

    def test_submit_accepts_json_command_line(self):
        surface, _, _, _ = self._surface()
        result = surface.handle_line('submit evaluate {"candidate_id":"candidate-1"}')
        self.assertIn('"operation": "EVALUATE"', result)
        self.assertIn('"status": "ACCEPTED"', result)

    def test_submit_invalid_json_is_surface_error(self):
        surface, _, _, _ = self._surface()
        with self.assertRaises(TerminalInterfaceError):
            surface.handle_line("submit PROPOSE {broken")

    def test_unknown_command_is_rejected(self):
        surface, _, _, _ = self._surface()
        with self.assertRaises(TerminalInterfaceError):
            surface.handle_line("dance")

    def test_activity_renders_session_only(self):
        surface, _, stream, projector = self._surface()
        surface.submit("PROPOSE", payload={})
        surface_other, _, _, _ = self._surface(session_id="other-session", actor_id="other-actor")
        self.assertNotIn("other-session", surface.render_activity())
        self.assertIn("REQUEST_RECEIVED", surface.render_activity())
        self.assertIn("RESPONSE_EMITTED", surface.render_activity())
        self.assertEqual(stream.size, 2)
        self.assertEqual(projector.state("session-256").latest_stage, "TEST_STAGE")
        self.assertEqual(surface_other.render_activity(), "NO ACTIVITY")

    def test_activity_limit_returns_latest_events(self):
        surface, _, _, _ = self._surface()
        surface.submit("PROPOSE", payload={})
        activity = surface.render_activity(limit=1)
        self.assertIn("RESPONSE_EMITTED", activity)
        self.assertNotIn("REQUEST_RECEIVED", activity)

    def test_status_is_derived_from_observed_session_state(self):
        surface, _, _, _ = self._surface()
        surface.submit("VERIFY", payload={})
        status = surface.handle_line("status")
        self.assertIn("SESSION session-256", status)
        self.assertIn("IDLE", status)
        self.assertIn("OPERATION VERIFY", status)
        self.assertIn("STAGE TEST_STAGE", status)

    def test_external_response_is_immutable(self):
        surface, _, _, _ = self._surface()
        response = surface.submit("PROPOSE", payload={})
        self.assertIsInstance(response, MappingProxyType)
        with self.assertRaises(TypeError):
            response["status"] = "FAILED"

    def test_run_provides_real_terminal_loop(self):
        surface, _, _, _ = self._surface()
        input_stream = io.StringIO("help\nstatus\nquit\n")
        output_stream = io.StringIO()
        surface.run(input_stream, output_stream)
        output = output_stream.getvalue()
        self.assertIn("JARVIS> READY", output)
        self.assertIn("COMMANDS:", output)
        self.assertIn("NO ACTIVITY", output)
        self.assertIn("BYE", output)

    def test_surface_has_no_authority_or_execution_powers(self):
        surface, _, _, _ = self._surface()
        self.assertFalse(surface.authorizes_execution)
        self.assertFalse(surface.executes_capability)
        self.assertFalse(surface.mutates_state)
        self.assertFalse(surface.persists_state)
        self.assertFalse(surface.establishes_truth)
        self.assertFalse(surface.establishes_certainty)
        self.assertFalse(surface.is_ai_provider)

    def test_request_ids_are_surface_local_and_incrementing(self):
        surface, orchestration, _, _ = self._surface()
        surface.submit("PROPOSE")
        surface.submit("EVALUATE")
        self.assertEqual([r.request_id for r in orchestration.requests], [
            "terminal-request-1",
            "terminal-request-2",
        ])

    def test_invalid_limit_is_rejected(self):
        surface, _, _, _ = self._surface()
        with self.assertRaises(ValueError):
            surface.render_activity(limit=0)
