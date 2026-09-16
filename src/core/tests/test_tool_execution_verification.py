import unittest

from src.core.tool_execution_verification import (
    ToolExecutionVerification,
    ToolVerificationStatus,
    require_verified,
)
from src.tools.models import ToolRequest, ToolResult


class ToolExecutionVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = ToolRequest(
            tool_name="read_status",
            arguments={"device": "ahu-1"},
            invocation_id="inv-1",
        )
        self.result = ToolResult(
            success=True,
            tool_name="read_status",
            content={"status": "running"},
            invocation_id="inv-1",
        )

    def test_verification_artifact_is_frozen(self) -> None:
        verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.VERIFIED,
            evidence="fresh device read matched expected state",
            reason="observed state matches the requested effect",
        )
        with self.assertRaises((AttributeError, TypeError)):
            verification.status = ToolVerificationStatus.FAILED  # type: ignore[misc]

    def test_result_must_match_request_identity(self) -> None:
        mismatched = ToolResult(
            success=True,
            tool_name="read_status",
            content={"status": "running"},
            invocation_id="other",
        )
        with self.assertRaises(ValueError):
            ToolExecutionVerification(
                request=self.request,
                result=mismatched,
                status=ToolVerificationStatus.VERIFIED,
                evidence="observation",
                reason="matched expected state",
            )

    def test_result_tool_name_mismatch_is_rejected(self) -> None:
        mismatched = ToolResult(
            success=True,
            tool_name="restart_device",
            content="ok",
            invocation_id="inv-1",
        )
        with self.assertRaises(ValueError):
            ToolExecutionVerification(
                request=self.request,
                result=mismatched,
                status=ToolVerificationStatus.VERIFIED,
                evidence="observation",
                reason="matched expected state",
            )

    def test_unverified_result_is_not_accepted_as_verified(self) -> None:
        verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.UNVERIFIED,
            evidence="tool reported success only",
            reason="no independent observation was performed",
        )
        with self.assertRaises(RuntimeError):
            require_verified(verification)

    def test_failed_verification_is_not_accepted(self) -> None:
        verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.FAILED,
            evidence="fresh read contradicted expected state",
            reason="requested effect was not observed",
        )
        with self.assertRaises(RuntimeError):
            require_verified(verification)

    def test_verified_requires_explicit_verified_status(self) -> None:
        verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.VERIFIED,
            evidence="fresh device read matched expected state",
            reason="independent observation confirmed the effect",
        )
        require_verified(verification)

    def test_empty_evidence_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ToolExecutionVerification(
                request=self.request,
                result=self.result,
                status=ToolVerificationStatus.VERIFIED,
                evidence=" ",
                reason="independent observation confirmed the effect",
            )

    def test_empty_reason_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ToolExecutionVerification(
                request=self.request,
                result=self.result,
                status=ToolVerificationStatus.VERIFIED,
                evidence="fresh device read matched expected state",
                reason=" ",
            )

    def test_verification_does_not_expose_execution_authority(self) -> None:
        verification = ToolExecutionVerification(
            request=self.request,
            result=self.result,
            status=ToolVerificationStatus.VERIFIED,
            evidence="fresh device read matched expected state",
            reason="independent observation confirmed the effect",
        )
        self.assertFalse(hasattr(verification, "invoke"))
        self.assertFalse(hasattr(verification, "authorize"))
        self.assertFalse(hasattr(verification, "confirm"))


if __name__ == "__main__":
    unittest.main()
