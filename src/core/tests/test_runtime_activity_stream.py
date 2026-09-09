import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
    SelfImprovementInterfaceBackend,
)
from src.core.self_improvement_orchestration import SelfImprovementOrchestration
from src.core.tests.test_continuous_self_improvement_candidate import M24_1ContinuousSelfImprovementCandidateTests
from src.core.tests.test_improvement_application import M24_4ImprovementApplicationTests
from src.core.tests.test_improvement_decision import M24_3ImprovementDecisionTests
from src.core.tests.test_improvement_evaluation import M24_2ImprovementEvaluationTests
from src.core.tests.test_improvement_verification import M24_5ImprovementVerificationRollbackTests
from src.core.self_improvement_orchestration import SelfImprovementOrchestration
from src.core.runtime_activity_stream import (
    InterfaceRuntimeActivityRecorder,
    ObservableInterfaceOrchestration,
    RuntimeActivityEvent,
    RuntimeActivityError,
    RuntimeActivityKind,
    RuntimeActivityStream,
)


class M25_3RuntimeActivityStreamTests(unittest.TestCase):
    def _request(self, operation=InterfaceOperation.STATUS, request_id="request-253"):
        return InterfaceRequest(
            request_id=request_id,
            session_id="session-253",
            actor_id="actor-253",
            operation=operation,
            payload={},
            metadata={"channel": "test"},
        )

    def _response(self, request, status=InterfaceResponseStatus.ACCEPTED, metadata=None):
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=status,
            payload={"ok": True},
            metadata=metadata or {"artifact_type": "TestArtifact"},
        )

    def test_event_is_typed_immutable_and_recursive(self):
        event = RuntimeActivityEvent(
            event_id="runtime-event-1",
            sequence=1,
            session_id="session",
            actor_id="actor",
            request_id="request",
            operation=InterfaceOperation.PROPOSE,
            kind=RuntimeActivityKind.REQUEST_RECEIVED,
            status=None,
            stage="INTERFACE_BACKEND",
            summary="received",
            metadata={"nested": [{"x": 1}]},
        )
        self.assertIsInstance(event.metadata, MappingProxyType)
        self.assertIsInstance(event.metadata["nested"], tuple)
        self.assertIsInstance(event.metadata["nested"][0], MappingProxyType)
        with self.assertRaises(TypeError):
            event.metadata["x"] = 1
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            event.summary = "changed"

    def test_event_requires_positive_sequence(self):
        with self.assertRaises(ValueError):
            RuntimeActivityEvent("e", 0, "s", "a", "r", InterfaceOperation.STATUS, RuntimeActivityKind.REQUEST_RECEIVED, None, "stage", "summary", {})

    def test_stream_requires_exact_event_type(self):
        stream = RuntimeActivityStream()
        with self.assertRaises(TypeError):
            stream.publish(object())

    def test_stream_requires_contiguous_sequence(self):
        stream = RuntimeActivityStream()
        request = self._request()
        event = InterfaceRuntimeActivityRecorder(stream).record_request(request)
        with self.assertRaises(RuntimeActivityError):
            stream.publish(RuntimeActivityEvent(
                event_id="runtime-event-3", sequence=3, session_id="s", actor_id="a", request_id="r",
                operation=InterfaceOperation.STATUS, kind=RuntimeActivityKind.REQUEST_RECEIVED,
                status=None, stage="stage", summary="gap", metadata={}
            ))
        self.assertEqual(event.sequence, 1)

    def test_snapshot_is_ordered_and_immutable(self):
        stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(stream)
        first = recorder.record_request(self._request(InterfaceOperation.PROPOSE, "request-1"))
        second = recorder.record_request(self._request(InterfaceOperation.EVALUATE, "request-2"))
        snapshot = stream.snapshot()
        self.assertEqual(snapshot, (first, second))
        self.assertIsInstance(snapshot, tuple)
        self.assertEqual([event.sequence for event in snapshot], [1, 2])

    def test_since_returns_only_later_events(self):
        stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(stream)
        recorder.record_request(self._request(request_id="request-1"))
        second = recorder.record_request(self._request(request_id="request-2"))
        self.assertEqual(stream.since(1), (second,))
        self.assertEqual(stream.since(2), ())

    def test_since_rejects_invalid_sequence(self):
        with self.assertRaises(ValueError):
            RuntimeActivityStream().since(-1)
        with self.assertRaises(ValueError):
            RuntimeActivityStream().since("1")

    def test_recorder_records_request_identity_and_operation(self):
        stream = RuntimeActivityStream()
        event = InterfaceRuntimeActivityRecorder(stream).record_request(self._request(InterfaceOperation.DECIDE))
        self.assertEqual(event.request_id, "request-253")
        self.assertEqual(event.session_id, "session-253")
        self.assertEqual(event.actor_id, "actor-253")
        self.assertIs(event.operation, InterfaceOperation.DECIDE)
        self.assertIs(event.kind, RuntimeActivityKind.REQUEST_RECEIVED)
        self.assertIsNone(event.status)

    def test_recorder_maps_response_status_to_activity_kind(self):
        stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(stream)
        for status, kind in (
            (InterfaceResponseStatus.ACCEPTED, RuntimeActivityKind.RESPONSE_EMITTED),
            (InterfaceResponseStatus.REJECTED, RuntimeActivityKind.REQUEST_REJECTED),
            (InterfaceResponseStatus.FAILED, RuntimeActivityKind.REQUEST_FAILED),
        ):
            request = self._request(request_id=f"request-{status.value.lower()}")
            event = recorder.record_response(request, self._response(request, status))
            self.assertIs(event.kind, kind)
            self.assertIs(event.status, status)

    def test_response_identity_mismatch_is_rejected(self):
        stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(stream)
        request = self._request()
        bad = InterfaceResponse("other", request.operation, InterfaceResponseStatus.ACCEPTED, {}, {})
        with self.assertRaises(RuntimeActivityError):
            recorder.record_response(request, bad)

    def test_observer_records_request_and_response_without_changing_result(self):
        class Port:
            def dispatch(self, request):
                return self._response(request)

            def _response(self, request):
                return InterfaceResponse(
                    request_id=request.request_id,
                    operation=request.operation,
                    status=InterfaceResponseStatus.ACCEPTED,
                    payload={"artifact": "opaque"},
                    metadata={"artifact_type": "Artifact"},
                )

        stream = RuntimeActivityStream()
        observer = ObservableInterfaceOrchestration(Port(), InterfaceRuntimeActivityRecorder(stream))
        request = self._request(InterfaceOperation.DECIDE)
        response = observer.dispatch(request)
        self.assertEqual(response.payload["artifact"], "opaque")
        self.assertEqual(stream.size, 2)
        events = stream.snapshot()
        self.assertIs(events[0].kind, RuntimeActivityKind.REQUEST_RECEIVED)
        self.assertIs(events[1].kind, RuntimeActivityKind.RESPONSE_EMITTED)
        self.assertEqual(events[1].stage, "Artifact")

    def test_observer_preserves_rejected_response(self):
        class Port:
            def dispatch(self, request):
                return InterfaceResponse(request.request_id, request.operation, InterfaceResponseStatus.REJECTED, {"error": "no"}, {})
        stream = RuntimeActivityStream()
        observer = ObservableInterfaceOrchestration(Port(), InterfaceRuntimeActivityRecorder(stream))
        response = observer.dispatch(self._request(InterfaceOperation.STATUS))
        self.assertIs(response.status, InterfaceResponseStatus.REJECTED)
        self.assertIs(stream.snapshot()[1].kind, RuntimeActivityKind.REQUEST_REJECTED)

    def test_observer_records_failure_event_and_re_raises_unexpected_exception(self):
        class Port:
            def dispatch(self, request):
                raise RuntimeError("boom")
        stream = RuntimeActivityStream()
        observer = ObservableInterfaceOrchestration(Port(), InterfaceRuntimeActivityRecorder(stream))
        with self.assertRaises(RuntimeError):
            observer.dispatch(self._request())
        self.assertEqual(stream.size, 2)
        self.assertIs(stream.snapshot()[1].kind, RuntimeActivityKind.REQUEST_FAILED)

    def test_observer_requires_valid_dependencies(self):
        with self.assertRaises(TypeError):
            ObservableInterfaceOrchestration(object(), InterfaceRuntimeActivityRecorder(RuntimeActivityStream()))
        with self.assertRaises(TypeError):
            ObservableInterfaceOrchestration(type("P", (), {"dispatch": lambda self, request: None})(), object())

    def test_stream_has_no_authority_or_persistence_powers(self):
        stream = RuntimeActivityStream()
        for name in ("authorizes_execution", "executes_capability", "mutates_state", "persists_state", "establishes_truth", "establishes_certainty"):
            self.assertFalse(hasattr(stream, name))


if __name__ == "__main__":
    unittest.main()
