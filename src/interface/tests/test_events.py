import json
import unittest

from src.interface.events import (
    InterfaceEvent,
    InterfaceEventKind,
    InterfaceEventRuntime,
    InterfaceEventStream,
)


class InterfaceEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = InterfaceEventRuntime()
        self.stream = self.runtime.start(
            request_id="req-1",
            event_id="evt-1",
            session_id="session-1",
            metadata={"surface": "chat"},
        )

    def test_start_creates_provider_neutral_stream(self) -> None:
        self.assertEqual(self.stream.request_id, "req-1")
        self.assertEqual(self.stream.session_id, "session-1")
        self.assertEqual(len(self.stream.events), 1)
        self.assertEqual(self.stream.latest.kind, InterfaceEventKind.RESPONSE_STARTED)
        self.assertEqual(self.stream.latest.sequence, 1)
        self.assertFalse(self.stream.terminal)

    def test_delta_appends_contiguous_ordered_event(self) -> None:
        stream = self.runtime.delta(
            self.stream,
            event_id="evt-2",
            content="hello",
        )
        self.assertEqual(tuple(event.sequence for event in stream.events), (1, 2))
        self.assertEqual(stream.latest.kind, InterfaceEventKind.CONTENT_DELTA)
        self.assertEqual(stream.latest.content, "hello")

    def test_multiple_deltas_preserve_order(self) -> None:
        stream = self.runtime.delta(self.stream, event_id="evt-2", content="hel")
        stream = self.runtime.delta(stream, event_id="evt-3", content="lo")
        self.assertEqual([event.content for event in stream.events[1:]], ["hel", "lo"])
        self.assertEqual([event.sequence for event in stream.events], [1, 2, 3])

    def test_complete_terminates_stream(self) -> None:
        stream = self.runtime.delta(self.stream, event_id="evt-2", content="answer")
        stream = self.runtime.complete(stream, event_id="evt-3", content="answer")
        self.assertTrue(stream.terminal)
        self.assertEqual(stream.latest.kind, InterfaceEventKind.RESPONSE_COMPLETED)
        self.assertEqual(stream.latest.sequence, 3)

    def test_failure_terminates_stream(self) -> None:
        stream = self.runtime.fail(
            self.stream,
            event_id="evt-2",
            content="request failed",
            metadata={"code": "TEMPORARY"},
        )
        self.assertTrue(stream.terminal)
        self.assertEqual(stream.latest.kind, InterfaceEventKind.RESPONSE_FAILED)
        self.assertEqual(stream.latest.metadata["code"], "TEMPORARY")

    def test_terminal_event_cannot_be_followed(self) -> None:
        stream = self.runtime.complete(self.stream, event_id="evt-2", content="done")
        with self.assertRaises(ValueError):
            self.runtime.delta(stream, event_id="evt-3", content="late")

    def test_sequence_must_be_contiguous(self) -> None:
        with self.assertRaises(ValueError):
            self.stream.append(
                InterfaceEvent(
                    event_id="evt-3",
                    request_id="req-1",
                    session_id="session-1",
                    kind=InterfaceEventKind.CONTENT_DELTA,
                    sequence=3,
                    content="out of order",
                )
            )

    def test_request_identity_must_match_stream(self) -> None:
        with self.assertRaises(ValueError):
            self.stream.append(
                InterfaceEvent(
                    event_id="evt-x",
                    request_id="other-request",
                    session_id="session-1",
                    kind=InterfaceEventKind.CONTENT_DELTA,
                    sequence=2,
                    content="wrong request",
                )
            )

    def test_session_identity_must_match_stream(self) -> None:
        with self.assertRaises(ValueError):
            self.stream.append(
                InterfaceEvent(
                    event_id="evt-x",
                    request_id="req-1",
                    session_id="other-session",
                    kind=InterfaceEventKind.CONTENT_DELTA,
                    sequence=2,
                    content="wrong session",
                )
            )

    def test_event_ids_are_unique(self) -> None:
        with self.assertRaises(ValueError):
            self.stream.append(
                InterfaceEvent(
                    event_id="evt-1",
                    request_id="req-1",
                    session_id="session-1",
                    kind=InterfaceEventKind.CONTENT_DELTA,
                    sequence=2,
                    content="duplicate id",
                )
            )

    def test_event_is_immutable(self) -> None:
        event = self.stream.latest
        with self.assertRaises(Exception):
            event.content = "changed"
        with self.assertRaises(TypeError):
            event.metadata["new"] = "value"

    def test_stream_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.stream.events = ()

    def test_invalid_event_payloads_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            InterfaceEvent(
                event_id="evt-x",
                request_id="req-1",
                kind=InterfaceEventKind.RESPONSE_STARTED,
                sequence=1,
                content="not allowed",
            )
        with self.assertRaises(ValueError):
            InterfaceEvent(
                event_id="evt-x",
                request_id="req-1",
                kind=InterfaceEventKind.CONTENT_DELTA,
                sequence=1,
                content="",
            )
        with self.assertRaises(ValueError):
            InterfaceEvent(
                event_id="evt-x",
                request_id="req-1",
                kind=InterfaceEventKind.RESPONSE_COMPLETED,
                sequence=1,
                content="",
            )

    def test_serialization_denies_semantic_authority(self) -> None:
        stream = self.runtime.delta(self.stream, event_id="evt-2", content="hello")
        payload = stream.to_dict()
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])
        for event in payload["events"]:
            self.assertFalse(event["authority_granted"])
            self.assertFalse(event["authorization_granted"])
            self.assertFalse(event["execution_requested"])

    def test_serialization_is_deterministic(self) -> None:
        stream = self.runtime.delta(self.stream, event_id="evt-2", content="hello")
        self.assertEqual(stream.to_json(), stream.to_json())
        self.assertEqual(json.loads(stream.to_json())["events"][0]["kind"], "RESPONSE_STARTED")

    def test_stream_event_bound_is_enforced(self) -> None:
        stream = InterfaceEventStream(request_id="req-2", max_events=1)
        stream = InterfaceEventRuntime().start(
            request_id="req-2", event_id="evt-1", max_events=1
        )
        with self.assertRaises(ValueError):
            InterfaceEventRuntime().delta(stream, event_id="evt-2", content="too many")

    def test_all_interface_event_kinds_are_transport_level(self) -> None:
        for kind in InterfaceEventKind:
            if kind is InterfaceEventKind.RESPONSE_STARTED:
                content = ""
            else:
                content = "event payload"
            event = InterfaceEvent(
                event_id=f"evt-{kind.value}",
                request_id="req-kinds",
                kind=kind,
                sequence=1,
                content=content,
            )
            payload = event.to_dict()
            self.assertFalse(payload["intent_interpreted"])
            self.assertFalse(payload["authority_granted"])
            self.assertFalse(payload["authorization_granted"])
            self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
