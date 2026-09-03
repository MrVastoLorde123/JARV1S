import json
import unittest

from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceRequest
from src.interface.request import InterfaceRequestBridge, JARVISRequest


class InterfaceRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.boundary = InterfaceBoundary()
        self.bridge = InterfaceRequestBridge()
        self.request = self.boundary.request(
            request_id=" req-1 ",
            channel=InterfaceChannel.TEXT,
            content="  handle this task  ",
            session_id=" session-1 ",
            metadata={"surface": "chat"},
        )

    def test_bridge_creates_provider_neutral_jarvis_request(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        self.assertIsInstance(result, JARVISRequest)
        self.assertEqual(result.request_id, "req-1")
        self.assertEqual(result.source_request_id, "req-1")
        self.assertEqual(result.content, "handle this task")
        self.assertEqual(result.channel, InterfaceChannel.TEXT)
        self.assertEqual(result.session_id, "session-1")

    def test_bridge_preserves_interface_identity(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        self.assertEqual(result.request_id, self.request.request_id)
        self.assertEqual(result.source_request_id, self.request.request_id)

    def test_bridge_preserves_metadata_without_mutation(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        self.assertEqual(result.metadata["surface"], "chat")
        with self.assertRaises(TypeError):
            result.metadata["new"] = "value"

    def test_jarvis_request_is_immutable(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        with self.assertRaises(Exception):
            result.content = "changed"

    def test_bridge_requires_interface_request(self) -> None:
        with self.assertRaises(TypeError):
            self.bridge.to_jarvis_request("not a request")

    def test_request_rejects_empty_identity_and_content(self) -> None:
        with self.assertRaises(ValueError):
            JARVISRequest("", "content", InterfaceChannel.TEXT)
        with self.assertRaises(ValueError):
            JARVISRequest("req", "", InterfaceChannel.TEXT)

    def test_request_rejects_invalid_channel(self) -> None:
        with self.assertRaises((TypeError, ValueError)):
            JARVISRequest("req", "content", "UNKNOWN")

    def test_request_serialization_denies_semantic_authority(self) -> None:
        payload = self.bridge.to_jarvis_request(self.request).to_dict()
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_request_serialization_is_deterministic(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        self.assertEqual(result.to_json(), result.to_json())
        self.assertEqual(json.loads(result.to_json())["request_id"], "req-1")

    def test_all_interface_channels_share_same_request_contract(self) -> None:
        for channel in InterfaceChannel:
            source = self.boundary.request(
                request_id=f"req-{channel.value.lower()}",
                channel=channel,
                content="same semantic payload",
            )
            result = self.bridge.to_jarvis_request(source)
            self.assertEqual(result.content, "same semantic payload")
            self.assertEqual(result.channel, channel)

    def test_bridge_does_not_invent_intent(self) -> None:
        source = self.boundary.request(
            request_id="req-2",
            channel=InterfaceChannel.TEXT,
            content="delete the file",
        )
        result = self.bridge.to_jarvis_request(source)
        self.assertEqual(result.content, "delete the file")
        payload = result.to_dict()
        self.assertFalse(payload["intent_interpreted"])

    def test_source_request_id_can_be_used_for_correlation(self) -> None:
        result = self.bridge.to_jarvis_request(self.request)
        self.assertEqual(result.source_request_id, result.request_id)


if __name__ == "__main__":
    unittest.main()
