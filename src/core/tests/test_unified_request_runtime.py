import unittest

from src.core.unified_request_runtime import UnifiedRequestResult, UnifiedRequestRuntime
from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceResponse
from src.interface.request import InterfaceRequestBridge, JARVISRequest


class FakeResponse:
    def __init__(self, content="processed", metadata=None):
        self.content = content
        self.metadata = metadata or {}


class FakeProcessor:
    def __init__(self):
        self.calls = []

    def ask(self, query: str) -> FakeResponse:
        self.calls.append(query)
        return FakeResponse(content=f"handled: {query}", metadata={"route": "CONVERSATION"})


class UnifiedRequestRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = FakeProcessor()
        self.runtime = UnifiedRequestRuntime(self.processor)
        self.request = JARVISRequest(
            request_id="req-1",
            content="hello JARVIS",
            channel=InterfaceChannel.TEXT,
            session_id="session-1",
            metadata={"model": "untrusted-request-metadata"},
        )

    def test_process_requires_jarvis_request(self) -> None:
        with self.assertRaises(TypeError):
            self.runtime.process("not a request")

    def test_process_sends_only_normalized_content_to_core(self) -> None:
        result = self.runtime.process(self.request)
        self.assertEqual(self.processor.calls, ["hello JARVIS"])
        self.assertIsInstance(result, UnifiedRequestResult)

    def test_process_preserves_request_and_session_identity(self) -> None:
        result = self.runtime.process(self.request)
        self.assertEqual(result.request_id, "req-1")
        self.assertEqual(result.session_id, "session-1")

    def test_request_metadata_cannot_select_provider(self) -> None:
        self.runtime.process(self.request)
        self.assertEqual(self.processor.calls, ["hello JARVIS"])

    def test_result_converts_to_interface_response(self) -> None:
        result = self.runtime.process(self.request)
        response = result.to_interface_response()
        self.assertIsInstance(response, InterfaceResponse)
        self.assertEqual(response.request_id, "req-1")
        self.assertEqual(response.content, "handled: hello JARVIS")
        self.assertEqual(response.metadata["session_id"], "session-1")
        self.assertEqual(response.metadata["integration"], "M12.1")

    def test_interface_response_preserves_non_authoritative_boundary(self) -> None:
        response = self.runtime.process(self.request).to_interface_response()
        payload = response.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_result_is_immutable(self) -> None:
        result = self.runtime.process(self.request)
        with self.assertRaises(Exception):
            result.request_id = "changed"

    def test_core_response_requires_non_empty_content_for_interface_projection(self) -> None:
        result = UnifiedRequestResult("req-1", "session-1", FakeResponse(content=""))
        with self.assertRaises(ValueError):
            result.to_interface_response()

    def test_processor_requires_ask_contract(self) -> None:
        with self.assertRaises(TypeError):
            UnifiedRequestRuntime(object())

    def test_core_exception_is_not_converted_into_authorization(self) -> None:
        class FailingProcessor:
            def ask(self, query):
                raise RuntimeError("core failure")

        runtime = UnifiedRequestRuntime(FailingProcessor())
        with self.assertRaises(RuntimeError):
            runtime.process(self.request)

    def test_interface_bridge_converges_into_unified_runtime(self) -> None:
        interface = InterfaceBoundary()
        bridge = InterfaceRequestBridge()
        source = interface.request(
            request_id="req-2",
            channel=InterfaceChannel.UI,
            content="show my task",
            session_id="session-2",
        )
        normalized = bridge.to_jarvis_request(source)
        result = self.runtime.process(normalized)
        response = result.to_interface_response()
        self.assertEqual(self.processor.calls, ["show my task"])
        self.assertEqual(response.request_id, "req-2")
        self.assertEqual(response.metadata["session_id"], "session-2")

    def test_runtime_does_not_create_a_second_semantic_path(self) -> None:
        self.runtime.process(self.request)
        self.assertEqual(len(self.processor.calls), 1)
        self.assertEqual(self.processor.calls[0], self.request.content)


if __name__ == "__main__":
    unittest.main()
