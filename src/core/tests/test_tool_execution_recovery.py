import unittest

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.core.tool_authorization_evidence_store import StoredToolAuthorizationEvidence
from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.core.tool_execution_chain import ToolExecutionChainTrace
from src.core.tool_execution_recovery import ToolExecutionRecoveryAction, ToolExecutionRecoveryService
from src.core.tool_execution_verification import ToolExecutionVerification, ToolVerificationStatus
from src.core.tool_execution_verification_evidence_store import StoredToolExecutionVerification
from src.tools.models import ToolRequest, ToolResult


class ToolExecutionRecoveryTests(unittest.TestCase):
    def _trace(self, status):
        request = ToolRequest(tool_name="ping_host", invocation_id="inv-1")
        result = ToolResult(success=True, tool_name="ping_host", invocation_id="inv-1", content={"ok": True})
        authorization = ToolExecutionAuthorization(
            step_id="step-1", request=request, authorized=True, policy_id="ops", reason="authorized"
        )
        auth_evidence = StoredToolAuthorizationEvidence(
            "auth-1",
            ToolAuthorizationEvidence(
                step_id="step-1", invocation_id="inv-1", tool_name="ping_host",
                scope="diagnostics", capability_class="diagnostic", authorized=True,
                policy_id="ops", reason="authorized",
            ),
        )
        verification = ToolExecutionVerification(
            request=request, result=result, status=status,
            evidence="evidence", reason="verification reason"
        )
        verification_evidence = StoredToolExecutionVerification("verify-1", verification)
        return ToolExecutionChainTrace(
            step=PlanStep(step_id="step-1", description="Ping", action="USE_TOOL", order=0),
            request=request,
            authorization=authorization,
            authorization_evidence=auth_evidence,
            result=result,
            verification=verification,
            verification_evidence=verification_evidence,
        )

    def test_verified_recommends_completion(self):
        result = ToolExecutionRecoveryService().recommend(self._trace(ToolVerificationStatus.VERIFIED))
        self.assertIs(ToolExecutionRecoveryAction.COMPLETE, result.action)
        self.assertFalse(result.authorizes_execution)
        self.assertFalse(result.authorizes_retry)

    def test_failed_recommends_correction_without_authority(self):
        result = ToolExecutionRecoveryService().recommend(self._trace(ToolVerificationStatus.FAILED))
        self.assertIs(ToolExecutionRecoveryAction.CORRECT, result.action)
        self.assertFalse(result.executes)
        self.assertFalse(result.authorizes_retry)

    def test_unverified_recommends_review(self):
        result = ToolExecutionRecoveryService().recommend(self._trace(ToolVerificationStatus.UNVERIFIED))
        self.assertIs(ToolExecutionRecoveryAction.REVIEW, result.action)

    def test_invalid_trace_is_rejected(self):
        with self.assertRaises(TypeError):
            ToolExecutionRecoveryService().recommend(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
