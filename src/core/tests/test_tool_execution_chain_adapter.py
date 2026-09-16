import unittest

from src.core.execution_plan_models import PlanStep
from src.core.plan_executor import PlanExecutor
from src.core.tool_execution_chain import ToolExecutionChain
from src.core.tool_execution_chain_adapter import ToolExecutionChainPlanHandler
from src.core.tool_execution_verification import ToolVerificationStatus
from src.core.tool_execution_verification_evidence_store import ToolExecutionVerificationEvidenceStore
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import StaticToolAuthorizationPolicy, ToolAuthorizationPolicyRule
from src.tools.models import ToolRequest, ToolResult


class FakeInvoker:
    def __init__(self):
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"ok": True},
            invocation_id=request.invocation_id,
        )


class FakeVerifier:
    def verify(self, request, result):
        from src.core.tool_execution_verification import ToolExecutionVerification

        return ToolExecutionVerification(
            request=request,
            result=result,
            status=ToolVerificationStatus.VERIFIED,
            evidence="independent check",
            reason="expected effect observed",
        )


class ToolExecutionChainAdapterTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path

        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        chain = ToolExecutionChain(
            invoker=FakeInvoker(),
            policy=StaticToolAuthorizationPolicy((ToolAuthorizationPolicyRule(
                policy_id="ops",
                scope="diagnostics",
                allowed_capability_classes=("diagnostic",),
                allowed_tools=("ping_host",),
            ),)),
            authorization_store=ToolAuthorizationEvidenceStore(base / "auth.db"),
            verifier=FakeVerifier(),
            verification_store=ToolExecutionVerificationEvidenceStore(base / "verify.db"),
        )
        self.handler = ToolExecutionChainPlanHandler(chain)
        self.step = PlanStep(
            step_id="step-1",
            description="Ping host",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "ping_host",
                "arguments": {"host": "127.0.0.1"},
                "scope": "diagnostics",
                "capability_class": "diagnostic",
            },
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_handler_returns_tool_content_and_exposes_trace(self):
        output = self.handler(self.step)
        self.assertEqual({"ok": True}, output)
        trace = self.handler.trace_for_step("step-1")
        self.assertIsNotNone(trace)
        self.assertTrue(trace.authorization.authorized)
        self.assertIs(ToolVerificationStatus.VERIFIED, trace.verification.status)

    def test_register_binds_use_tool_action(self):
        executor = PlanExecutor()
        self.handler.register(executor)
        self.assertTrue(executor.has_handler("USE_TOOL"))

    def test_missing_step_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.handler.trace_for_step("")

    def test_invalid_chain_and_executor_are_rejected(self):
        with self.assertRaises(TypeError):
            ToolExecutionChainPlanHandler(object())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.handler.register(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
