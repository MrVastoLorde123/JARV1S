import json
import unittest

from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.session import ConversationSession, ConversationTurn, SessionConflictError, SessionRuntime, SessionStore


class SessionRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.boundary = InterfaceBoundary()
        self.runtime = SessionRuntime()
        self.request = self.boundary.request(
            request_id="req-1",
            channel=InterfaceChannel.TEXT,
            content="  hello JARVIS  ",
        )
        self.response = self.boundary.response(
            request_id="req-1",
            content="Hello.",
        )

    def test_session_requires_non_empty_identity(self) -> None:
        with self.assertRaises(ValueError):
            ConversationSession("")

    def test_session_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            ConversationSession("session-1", max_turns=0)

    def test_receive_binds_missing_session_id(self) -> None:
        session = ConversationSession("session-1")
        updated = self.runtime.receive(session, self.request)
        self.assertEqual(updated.turns[0].request.session_id, "session-1")
        self.assertEqual(updated.turns[0].request.content, "hello JARVIS")

    def test_receive_rejects_wrong_session(self) -> None:
        session = ConversationSession("session-1")
        request = self.boundary.request(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="hello",
            session_id="session-2",
        )
        with self.assertRaises(ValueError):
            self.runtime.receive(session, request)

    def test_duplicate_request_identity_is_rejected(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        with self.assertRaises(SessionConflictError):
            self.runtime.receive(session, self.request)

    def test_response_must_correlate_to_latest_request(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        wrong = self.boundary.response(request_id="other", content="no")
        with self.assertRaises(ValueError):
            self.runtime.respond(session, wrong)

    def test_response_completes_latest_turn(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        updated = self.runtime.respond(session, self.response)
        self.assertTrue(updated.turns[0].complete)
        self.assertEqual(updated.turns[0].response.request_id, "req-1")

    def test_response_cannot_be_added_twice(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        completed = self.runtime.respond(session, self.response)
        with self.assertRaises(SessionConflictError):
            self.runtime.respond(completed, self.response)

    def test_turn_requires_matching_request_and_response_ids(self) -> None:
        wrong = self.boundary.response(request_id="req-2", content="no")
        with self.assertRaises(ValueError):
            ConversationTurn(self.request, wrong)

    def test_turn_history_preserves_order_and_is_immutable(self) -> None:
        session = self.runtime.respond(
            self.runtime.receive(ConversationSession("session-1"), self.request),
            self.response,
        )
        second_request = self.boundary.request(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="second",
            session_id="session-1",
        )
        session = self.runtime.receive(session, second_request)
        self.assertEqual(
            tuple(turn.request.request_id for turn in session.turns),
            ("req-1", "req-2"),
        )
        with self.assertRaises(TypeError):
            session.turns[0] = session.turns[1]

    def test_turn_bound_stops_new_requests(self) -> None:
        session = ConversationSession("session-1", max_turns=1)
        session = self.runtime.receive(session, self.request)
        second_request = self.boundary.request(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="second",
            session_id="session-1",
        )
        with self.assertRaises(ValueError):
            self.runtime.receive(session, second_request)

    def test_store_is_immutable_and_conflict_aware(self) -> None:
        store = SessionStore()
        session = store.open("session-1")
        store = store.append(session)
        with self.assertRaises(SessionConflictError):
            store.append(session)
        updated = self.runtime.receive(session, self.request)
        replaced = store.replace(updated)
        self.assertEqual(replaced.get("session-1"), updated)
        self.assertNotEqual(store.get("session-1"), updated)

    def test_session_serialization_has_no_authority_or_execution_semantics(self) -> None:
        session = self.runtime.respond(
            self.runtime.receive(ConversationSession("session-1"), self.request),
            self.response,
        )
        payload = json.loads(session.to_json())
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_runtime_does_not_interpret_intent(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        self.assertEqual(session.turns[0].request.content, "hello JARVIS")
        self.assertFalse(session.turns[0].request.to_dict()["intent_interpreted"])

    def test_pending_request_is_explicit(self) -> None:
        session = self.runtime.receive(ConversationSession("session-1"), self.request)
        self.assertEqual(session.pending_request(), session.turns[0].request)
        session = self.runtime.respond(session, self.response)
        self.assertIsNone(session.pending_request())

    def test_empty_session_has_no_latest_turn(self) -> None:
        session = ConversationSession("session-1")
        self.assertIsNone(session.latest())
        self.assertIsNone(session.pending_request())


if __name__ == "__main__":
    unittest.main()
