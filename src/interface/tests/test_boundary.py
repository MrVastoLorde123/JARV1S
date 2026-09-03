import json
import unittest

from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceRequest, InterfaceResponse


class InterfaceBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.boundary = InterfaceBoundary()

    def test_request_is_immutable_and_normalized(self) -> None:
        request = self.boundary.request(
            request_id=" req-1 ",
            channel=InterfaceChannel.TEXT,
            content="  hello JARVIS  ",
            session_id=" session-1 ",
            metadata={"client": "chat"},
        )
        self.assertIsInstance(request, InterfaceRequest)
        self.assertEqual(request.request_id, "req-1")
        self.assertEqual(request.content, "hello JARVIS")
        self.assertEqual(request.session_id, "session-1")
        with self.assertRaises(TypeError):
            request.metadata["x"] = "y"

    def test_supported_channels_share_one_request_shape(self) -> None:
        requests = tuple(
            self.boundary.request(
                request_id=f"req-{channel.value}",
                channel=channel,
                content="same interaction",
            )
            for channel in (
                InterfaceChannel.TEXT,
                InterfaceChannel.VOICE,
                InterfaceChannel.UI,
                InterfaceChannel.API,
            )
        )
        self.assertEqual(tuple(item.content for item in requests), ("same interaction",) * 4)

    def test_interface_does_not_interpret_intent(self) -> None:
        request = self.boundary.request(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="delete the old server",
        )
        payload = request.to_dict()
        self.assertFalse(payload["intent_interpreted"])

    def test_interface_does_not_create_authority_or_execution(self) -> None:
        request = self.boundary.request(
            request_id="req-3",
            channel=InterfaceChannel.API,
            content="run this",
        )
        payload = request.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_input_requires_non_empty_content_and_identity(self) -> None:
        with self.assertRaises(ValueError):
            self.boundary.request(
                request_id="",
                channel=InterfaceChannel.TEXT,
                content="hello",
            )
        with self.assertRaises(ValueError):
            self.boundary.request(
                request_id="req-4",
                channel=InterfaceChannel.TEXT,
                content="   ",
            )

    def test_session_id_is_optional_but_bounded(self) -> None:
        request = self.boundary.request(
            request_id="req-5",
            channel=InterfaceChannel.UI,
            content="hello",
        )
        self.assertIsNone(request.session_id)
        with self.assertRaises(ValueError):
            self.boundary.request(
                request_id="req-6",
                channel=InterfaceChannel.UI,
                content="hello",
                session_id="   ",
            )

    def test_invalid_channel_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.boundary.request(
                request_id="req-7",
                channel="terminal",
                content="hello",
            )

    def test_metadata_is_provider_neutral_and_preserved(self) -> None:
        request = self.boundary.request(
            request_id="req-8",
            channel=InterfaceChannel.OTHER,
            content="hello",
            metadata={"provider": "custom-client", "locale": "en"},
        )
        self.assertEqual(request.metadata["provider"], "custom-client")
        self.assertEqual(request.metadata["locale"], "en")

    def test_response_is_immutable_and_request_correlated(self) -> None:
        response = self.boundary.response(
            request_id="req-9",
            content="done",
            metadata={"format": "text"},
        )
        self.assertIsInstance(response, InterfaceResponse)
        self.assertEqual(response.request_id, "req-9")
        self.assertEqual(response.content, "done")
        with self.assertRaises(TypeError):
            response.metadata["x"] = "y"

    def test_response_cannot_grant_authority_or_execution(self) -> None:
        response = self.boundary.response(request_id="req-10", content="action complete")
        payload = response.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_serialization_is_deterministic(self) -> None:
        request = self.boundary.request(
            request_id="req-11",
            channel=InterfaceChannel.TEXT,
            content="hello",
            metadata={"b": 2, "a": 1},
        )
        first = request.to_json()
        second = request.to_json()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["channel"], "TEXT")

    def test_boundary_does_not_require_a_specific_ai_provider(self) -> None:
        request = self.boundary.request(
            request_id="req-12",
            channel=InterfaceChannel.API,
            content="future reasoning request",
            metadata={"model": "any-provider"},
        )
        self.assertEqual(request.metadata["model"], "any-provider")
        self.assertNotIn("provider_sdk", request.to_dict())


if __name__ == "__main__":
    unittest.main()
