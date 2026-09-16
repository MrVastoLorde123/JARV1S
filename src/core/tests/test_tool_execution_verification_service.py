import unittest

from src.core.tool_execution_verification import (
    ToolExecutionVerification,
    ToolVerificationStatus,
)
from src.core.tool_execution_verification_service import ToolExecutionVerificationService
from src.tools.models import ToolRequest, ToolResult


class FakeVerifier:
    def __init__(self, verification):
        self.verification = verification
        self.calls = []

    def verify(self, request, result):
        self.calls.append((request, result))
        return self.verification


class ToolExecutionVerificationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = ToolRequest(tool_name="read_status", invocation_id="inv-1")
        self.result = ToolResult(
            success=True,
            tool_name="read_status",
            content={"status": "running"},
            invocation_id="inv-1",
        )
        self.verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.UNVERIFIED,
            evidence="tool result only",
            reason="no independent observation was performed",
        )
        self.verifier = FakeVerifier(self.verification)
        self.service = ToolExecutionVerificationService(self.verifier)

    def test_service_delegates_exact_request_and_result(self) -> None:
        returned = self.service.verify(self.request, self.result)
        self.assertEqual(self.verification, returned)
        self.assertEqual([(self.request, self.result)], self.verifier.calls)

    def test_service_rejects_mismatched_tool_name(self) -> None:
        result = ToolResult(
            success=True,
            tool_name="restart_device",
            content="ok",
            invocation_id="inv-1",
        )
        with self.assertRaises(ValueError):
            self.service.verify(self.request, result)
        self.assertEqual([], self.verifier.calls)

    def test_service_rejects_mismatched_invocation_id(self) -> None:
        result = ToolResult(
            success=True,
            tool_name="read_status",
            content="ok",
            invocation_id="other",
        )
        with self.assertRaises(ValueError):
            self.service.verify(self.request, result)
        self.assertEqual([], self.verifier.calls)

    def test_service_rejects_invalid_verifier_output(self) -> None:
        self.verifier.verification = object()
        with self.assertRaises(TypeError):
            self.service.verify(self.request, self.result)

    def test_service_does_not_execute_or_authorize(self) -> None:
        self.service.verify(self.request, self.result)
        self.assertFalse(hasattr(self.service, "invoke"))
        self.assertFalse(hasattr(self.service, "authorize"))


if __name__ == "__main__":
    unittest.main()
