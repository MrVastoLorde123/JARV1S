import unittest

from src.core.models import JARVISResponse
from src.core.unified_request_runtime import UnifiedRequestRuntime
from src.interface.boundary import InterfaceChannel
from src.interface.request import JARVISRequest


class _RecordingProcessor:
    def __init__(self) -> None:
        self.calls = []

    def ask(self, query: str) -> JARVISResponse:
        self.calls.append(query)
        return JARVISResponse(
            content="processed",
            ai_response=None,
            context=None,
            metadata={"route": "CONVERSATION"},
        )


class UnifiedRequestRuntimeCanonicalCognitionTests(unittest.TestCase):
    def test_cognition_runs_before_core_processor_and_is_attached_as_metadata(self) -> None:
        processor = _RecordingProcessor()
        runtime = UnifiedRequestRuntime(processor)
        request = JARVISRequest(
            request_id="request-unified-cs1",
            channel=InterfaceChannel.UI,
            content="prepare a safe next step",
            session_id="session-unified-cs1",
        )

        result = runtime.process(request)
        metadata = result.core_response.metadata["canonical_cognition"]

        self.assertEqual(processor.calls, ["prepare a safe next step"])
        self.assertEqual(metadata["request_id"], "request-unified-cs1")
        self.assertEqual(
            metadata["stage_sequence"],
            ("context", "world_model", "reasoning", "planning", "initiative"),
        )
        self.assertIsNotNone(metadata["proposal_id"])
        self.assertFalse(metadata["authority_granted"])
        self.assertFalse(metadata["authorization_granted"])
        self.assertFalse(metadata["execution_requested"])

    def test_command_input_does_not_enter_cognitive_chain(self) -> None:
        processor = _RecordingProcessor()
        runtime = UnifiedRequestRuntime(processor)
        request = JARVISRequest(
            request_id="request-command-cs1",
            channel=InterfaceChannel.TEXT,
            content="/CANCEL",
        )

        result = runtime.process(request)

        self.assertEqual(processor.calls, ["/CANCEL"])
        self.assertNotIn("canonical_cognition", result.core_response.metadata)


if __name__ == "__main__":
    unittest.main()
