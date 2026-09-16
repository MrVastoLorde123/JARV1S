import unittest

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.core.tool_authorization_evidence_store import StoredToolAuthorizationEvidence
from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.core.tool_execution_chain import ToolExecutionChainTrace
from src.core.tool_execution_learning_signal import ToolExecutionLearningSignalService
from src.core.tool_execution_verification import ToolExecutionVerification, ToolVerificationStatus
from src.core.tool_execution_verification_evidence_store import StoredToolExecutionVerification
from src.tools.models import ToolRequest, ToolResult


class ToolExecutionLearningSignalTests(unittest.TestCase):
    def _trace(self, status=ToolVerificationStatus.VERIFIED):
        request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="inv-1",
        )
        result = ToolResult(
            success=True,
            tool_name="ping_host",
            content={"reachable": True},
            invocation_id="inv-1",
        )
        authorization = ToolExecutionAuthorization(
            step_id="step-1",
            request=request,
            authorized=True,
            policy_id="ops-read",
            reason="authorized",
        )
        authorization_evidence = StoredToolAuthorizationEvidence(
            "auth-evidence-id",
            ToolAuthorizationEvidence(
                step_id="step-1",
                invocation_id="inv-1",
                tool_name="ping_host",
                scope="diagnostics",
                capability_class="diagnostic",
                authorized=True,
                policy_id="ops-read",
                reason="authorized",
            ),
        )
        verification = ToolExecutionVerification(
            request=request,
            result=result,
            status=status,
            evidence="verification evidence",
            reason="verification reason",
        )
        verification_evidence = StoredToolExecutionVerification(
            "verification-evidence-id", verification
        )
        return ToolExecutionChainTrace(
            step=PlanStep(
                step_id="step-1",
                description="Ping host",
                action="USE_TOOL",
                order=0,
            ),
            request=request,
            authorization=authorization,
            authorization_evidence=authorization_evidence,
            result=result,
            verification=verification,
            verification_evidence=verification_evidence,
        )

    def test_signal_is_inert_and_preserves_verification_status(self):
        signal = ToolExecutionLearningSignalService().create(
            self._trace(), signal_id="signal-1"
        )
        self.assertTrue(signal.authorized)
        self.assertTrue(signal.execution_succeeded)
        self.assertTrue(signal.verified)
        self.assertIs(ToolVerificationStatus.VERIFIED, signal.verification_status)
        self.assertFalse(signal.establishes_truth)
        self.assertFalse(signal.authorizes_execution)
        self.assertFalse(signal.authorizes_retry)
        self.assertFalse(signal.updates_model)
        self.assertFalse(signal.mutates_memory)
        self.assertEqual("auth-evidence-id", signal.lineage["authorization_evidence_id"])
        self.assertEqual("verification-evidence-id", signal.lineage["verification_evidence_id"])

    def test_unverified_outcome_never_becomes_verified_signal(self):
        signal = ToolExecutionLearningSignalService().create(
            self._trace(ToolVerificationStatus.UNVERIFIED), signal_id="signal-2"
        )
        self.assertFalse(signal.verified)
        self.assertIs(ToolVerificationStatus.UNVERIFIED, signal.verification_status)

    def test_signal_requires_chain_trace_and_identity(self):
        service = ToolExecutionLearningSignalService()
        with self.assertRaises(TypeError):
            service.create(object(), signal_id="signal-3")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            service.create(self._trace(), signal_id="")


if __name__ == "__main__":
    unittest.main()
