import json
import unittest

from src.interface.boundary import InterfaceChannel
from src.interface.multimodal import (
    InterfaceModality,
    ModalityDescriptor,
    MultiModalRuntime,
)
from src.interface.request import JARVISRequest


class MultiModalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = MultiModalRuntime()
        self.text = ModalityDescriptor(
            modality=InterfaceModality.TEXT,
            media_type="text/plain",
            payload_ref="payload:text-1",
            metadata={"lang": "en"},
        )
        self.image = ModalityDescriptor(
            modality=InterfaceModality.IMAGE,
            media_type="image/png",
            payload_ref="blob:image-1",
        )
        self.request = self.runtime.create(
            request_id="req-1",
            content="Please inspect these.",
            channel=InterfaceChannel.UI,
            modalities=(self.text, self.image),
            session_id="session-1",
            metadata={"surface": "chat"},
        )

    def test_descriptor_is_immutable(self) -> None:
        with self.assertRaises(Exception):
            self.text.payload_ref = "changed"
        with self.assertRaises(TypeError):
            self.text.metadata["x"] = "y"

    def test_supported_modalities_share_one_descriptor_contract(self) -> None:
        for modality in InterfaceModality:
            descriptor = ModalityDescriptor(
                modality=modality,
                media_type="application/octet-stream",
                payload_ref=f"payload:{modality.value.lower()}",
            )
            self.assertEqual(descriptor.modality, modality)

    def test_request_is_immutable_and_bounded(self) -> None:
        with self.assertRaises(Exception):
            self.request.content = "changed"
        with self.assertRaises(ValueError):
            self.runtime.create(
                request_id="req-x",
                content="x",
                channel=InterfaceChannel.UI,
                modalities=(self.text,),
                max_modalities=0,
            )

    def test_request_rejects_modalities_above_bound(self) -> None:
        with self.assertRaises(ValueError):
            self.runtime.create(
                request_id="req-x",
                content="x",
                channel=InterfaceChannel.UI,
                modalities=(self.text, self.image),
                max_modalities=1,
            )

    def test_add_modality_preserves_order_and_identity(self) -> None:
        request = self.runtime.create(
            request_id="req-2",
            content="inspect",
            channel=InterfaceChannel.TEXT,
        )
        request = self.runtime.add_modality(request, self.text)
        request = self.runtime.add_modality(request, self.image)
        self.assertEqual(request.request_id, "req-2")
        self.assertEqual(request.channel, InterfaceChannel.TEXT)
        self.assertEqual(
            [item.payload_ref for item in request.modalities],
            ["payload:text-1", "blob:image-1"],
        )

    def test_add_modality_enforces_bound(self) -> None:
        request = self.runtime.create(
            request_id="req-3",
            content="inspect",
            channel=InterfaceChannel.TEXT,
            max_modalities=1,
        )
        request = self.runtime.add_modality(request, self.text)
        with self.assertRaises(ValueError):
            self.runtime.add_modality(request, self.image)

    def test_descriptor_requires_non_empty_reference_and_media_type(self) -> None:
        with self.assertRaises(ValueError):
            ModalityDescriptor(InterfaceModality.FILE, "", "ref")
        with self.assertRaises(ValueError):
            ModalityDescriptor(InterfaceModality.FILE, "text/plain", "")

    def test_request_converges_to_existing_jarvis_request_contract(self) -> None:
        result = self.request.to_jarvis_request()
        self.assertIsInstance(result, JARVISRequest)
        self.assertEqual(result.request_id, "req-1")
        self.assertEqual(result.source_request_id, "req-1")
        self.assertEqual(result.content, "Please inspect these.")
        self.assertEqual(result.channel, InterfaceChannel.UI)
        self.assertEqual(len(result.metadata["modalities"]), 2)

    def test_projection_does_not_interpret_intent_or_grant_authority(self) -> None:
        result = self.request.to_jarvis_request()
        payload = result.to_dict()
        self.assertFalse(payload["intent_interpreted"])
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])
        self.assertEqual(
            payload["metadata"]["modalities"][1]["modality"], "IMAGE"
        )

    def test_modality_payload_is_reference_not_embedded_media(self) -> None:
        payload = self.request.to_dict()
        self.assertEqual(payload["modalities"][0]["payload_ref"], "payload:text-1")
        self.assertNotIn("bytes", payload["modalities"][0])
        self.assertNotIn("data", payload["modalities"][0])

    def test_metadata_is_preserved_without_mutation(self) -> None:
        self.assertEqual(self.request.metadata["surface"], "chat")
        with self.assertRaises(TypeError):
            self.request.metadata["new"] = "value"

    def test_serialization_is_deterministic(self) -> None:
        self.assertEqual(self.request.to_json(), self.request.to_json())
        payload = json.loads(self.request.to_json())
        self.assertEqual(payload["channel"], "UI")
        self.assertEqual(payload["modalities"][0]["media_type"], "text/plain")
        self.assertEqual(payload["modalities"][1]["modality"], "IMAGE")

    def test_runtime_requires_correct_types(self) -> None:
        with self.assertRaises(TypeError):
            self.runtime.add_modality("not a request", self.text)
        with self.assertRaises(TypeError):
            self.runtime.add_modality(self.request, "not a descriptor")

    def test_invalid_modality_is_rejected(self) -> None:
        with self.assertRaises((TypeError, ValueError)):
            ModalityDescriptor("UNKNOWN", "text/plain", "ref")

    def test_invalid_channel_is_rejected(self) -> None:
        with self.assertRaises((TypeError, ValueError)):
            self.runtime.create(
                request_id="req-invalid",
                content="x",
                channel="UNKNOWN",
            )


if __name__ == "__main__":
    unittest.main()
