import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceResponseStatus,
)
from src.core.interface_session_state import (
    InterfaceSessionState,
    InterfaceSessionStateError,
    InterfaceSessionStateProjector,
)
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind


class M25_4InterfaceSessionStateTests(unittest.TestCase):
    def _event(
        self,
        sequence,
        *,
        session_id="session-254",
        actor_id="actor-254",
        request_id=None,
        operation=InterfaceOperation.PROPOSE,
        kind=RuntimeActivityKind.REQUEST_RECEIVED,
        status=None,
        stage="INTERFACE_BACKEND",
    ):
        return RuntimeActivityEvent(
            event_id=f"runtime-event-{sequence}",
            sequence=sequence,
            session_id=session_id,
            actor_id=actor_id,
            request_id=request_id or f"request-{sequence}",
            operation=operation,
            kind=kind,
            status=status,
            stage=stage,
            summary="observed",
            metadata={"source": "test", "nested": [{"ok": True}]},
        )

    def test_state_is_typed_immutable_and_recursive(self):
        projector = InterfaceSessionStateProjector()
        state = projector.apply(self._event(1))
        self.assertIsInstance(state, InterfaceSessionState)
        self.assertIsInstance(state.metadata, MappingProxyType)
        self.assertIsInstance(state.metadata["latest_event_kind"], str)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            state.event_count = 2
        with self.assertRaises(TypeError):
            state.metadata["x"] = 1

    def test_empty_session_is_unknown(self):
        projector = InterfaceSessionStateProjector()
        self.assertIsNone(projector.state("missing-session"))
        self.assertEqual(projector.session_count, 0)

    def test_first_event_establishes_session_view(self):
        projector = InterfaceSessionStateProjector()
        state = projector.apply(self._event(1))
        self.assertEqual(state.session_id, "session-254")
        self.assertEqual(state.actor_id, "actor-254")
        self.assertEqual(state.event_count, 1)
        self.assertEqual(state.first_sequence, 1)
        self.assertEqual(state.last_sequence, 1)
        self.assertEqual(state.latest_event_id, "runtime-event-1")
        self.assertTrue(state.is_active)

    def test_response_event_closes_observed_activity(self):
        projector = InterfaceSessionStateProjector()
        projector.apply(self._event(1))
        state = projector.apply(
            self._event(
                2,
                kind=RuntimeActivityKind.RESPONSE_EMITTED,
                status=InterfaceResponseStatus.ACCEPTED,
                request_id="request-1",
                stage="ContinuousSelfImprovementCandidate",
            )
        )
        self.assertFalse(state.is_active)
        self.assertEqual(state.latest_status, InterfaceResponseStatus.ACCEPTED)
        self.assertEqual(state.latest_stage, "ContinuousSelfImprovementCandidate")
        self.assertEqual(state.latest_request_id, "request-1")

    def test_rejected_and_failed_events_are_inactive(self):
        for kind, status in (
            (RuntimeActivityKind.REQUEST_REJECTED, InterfaceResponseStatus.REJECTED),
            (RuntimeActivityKind.REQUEST_FAILED, InterfaceResponseStatus.FAILED),
        ):
            projector = InterfaceSessionStateProjector()
            projector.apply(self._event(1))
            state = projector.apply(
                self._event(2, kind=kind, status=status, request_id="request-1")
            )
            self.assertFalse(state.is_active)
            self.assertEqual(state.latest_kind, kind)
            self.assertEqual(state.latest_status, status)

    def test_sessions_are_isolated(self):
        projector = InterfaceSessionStateProjector()
        first = projector.apply(self._event(1, session_id="session-a", actor_id="actor-a"))
        second = projector.apply(self._event(2, session_id="session-b", actor_id="actor-b"))
        self.assertEqual(first.session_id, "session-a")
        self.assertEqual(second.session_id, "session-b")
        self.assertEqual(projector.state("session-a").event_count, 1)
        self.assertEqual(projector.state("session-b").event_count, 1)
        self.assertEqual(projector.session_count, 2)

    def test_actor_identity_cannot_change_within_session(self):
        projector = InterfaceSessionStateProjector()
        projector.apply(self._event(1, actor_id="actor-a"))
        with self.assertRaises(InterfaceSessionStateError):
            projector.apply(self._event(2, actor_id="actor-b"))
        self.assertEqual(projector.state("session-254").event_count, 1)

    def test_session_sequence_must_advance_strictly(self):
        projector = InterfaceSessionStateProjector()
        projector.apply(self._event(3))
        with self.assertRaises(InterfaceSessionStateError):
            projector.apply(self._event(2))
        with self.assertRaises(InterfaceSessionStateError):
            projector.apply(self._event(3))

    def test_interleaved_sessions_allow_global_sequence_gaps(self):
        projector = InterfaceSessionStateProjector()
        projector.apply(self._event(1, session_id="session-a", actor_id="actor-a"))
        projector.apply(self._event(2, session_id="session-b", actor_id="actor-b"))
        state = projector.apply(
            self._event(
                3,
                session_id="session-a",
                actor_id="actor-a",
                operation=InterfaceOperation.EVALUATE,
                kind=RuntimeActivityKind.RESPONSE_EMITTED,
                status=InterfaceResponseStatus.ACCEPTED,
                request_id="request-a",
                stage="ImprovementEvaluation",
            )
        )
        self.assertEqual(state.event_count, 2)
        self.assertEqual(state.first_sequence, 1)
        self.assertEqual(state.last_sequence, 3)
        self.assertFalse(state.is_active)

    def test_snapshot_is_immutable(self):
        projector = InterfaceSessionStateProjector()
        projector.apply(self._event(1))
        snapshot = projector.snapshot()
        self.assertIsInstance(snapshot, MappingProxyType)
        with self.assertRaises(TypeError):
            snapshot["other"] = self._event(99)
        self.assertEqual(snapshot["session-254"].event_count, 1)

    def test_project_consumes_immutable_event_tuple(self):
        projector = InterfaceSessionStateProjector()
        events = (
            self._event(1, session_id="session-a", actor_id="actor-a"),
            self._event(2, session_id="session-a", actor_id="actor-a"),
        )
        snapshot = projector.project(events)
        self.assertEqual(snapshot["session-a"].event_count, 2)
        self.assertEqual(snapshot["session-a"].first_sequence, 1)
        self.assertEqual(snapshot["session-a"].last_sequence, 2)

    def test_project_interleaved_sessions(self):
        projector = InterfaceSessionStateProjector()
        events = (
            self._event(1, session_id="session-a", actor_id="actor-a"),
            self._event(2, session_id="session-b", actor_id="actor-b"),
            self._event(
                3,
                session_id="session-a",
                actor_id="actor-a",
                kind=RuntimeActivityKind.RESPONSE_EMITTED,
                status=InterfaceResponseStatus.ACCEPTED,
            ),
        )
        snapshot = projector.project(events)
        self.assertEqual(snapshot["session-a"].event_count, 2)
        self.assertEqual(snapshot["session-a"].last_sequence, 3)
        self.assertEqual(snapshot["session-b"].event_count, 1)

    def test_project_requires_tuple(self):
        projector = InterfaceSessionStateProjector()
        with self.assertRaises(TypeError):
            projector.project([self._event(1)])

    def test_exact_event_type_is_required(self):
        projector = InterfaceSessionStateProjector()
        with self.assertRaises(TypeError):
            projector.apply(object())

    def test_session_identifier_validation(self):
        projector = InterfaceSessionStateProjector()
        with self.assertRaises(ValueError):
            projector.state("")
        with self.assertRaises(ValueError):
            projector.state("   ")

    def test_latest_activity_replaces_only_derived_fields(self):
        projector = InterfaceSessionStateProjector()
        first = projector.apply(self._event(1, operation=InterfaceOperation.PROPOSE))
        second = projector.apply(
            self._event(
                2,
                operation=InterfaceOperation.EVALUATE,
                kind=RuntimeActivityKind.RESPONSE_EMITTED,
                status=InterfaceResponseStatus.ACCEPTED,
                request_id="request-2",
                stage="ImprovementEvaluation",
            )
        )
        self.assertEqual(second.first_sequence, first.first_sequence)
        self.assertEqual(second.event_count, 2)
        self.assertEqual(second.latest_operation, InterfaceOperation.EVALUATE)
        self.assertEqual(second.latest_event_id, "runtime-event-2")

    def test_non_authoritative_and_non_persistent_walls(self):
        projector = InterfaceSessionStateProjector()
        self.assertFalse(projector.authorizes_execution)
        self.assertFalse(projector.executes_capability)
        self.assertFalse(projector.mutates_runtime_state)
        self.assertFalse(projector.persists_state)
        self.assertFalse(projector.establishes_truth)
        self.assertFalse(projector.establishes_certainty)
        self.assertFalse(projector.is_ai_provider)
