import tempfile
import unittest
from pathlib import Path

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import StaticToolAuthorizationPolicy, ToolAuthorizationPolicyRule
from src.core.tool_execution import ToolExecutionConfirmation
from src.core.tool_execution_chain import ToolExecutionChain
from src.core.tool_execution_verification import ToolExecutionVerification, ToolVerificationStatus
from src.core.tool_execution_verification_evidence_store import ToolExecutionVerificationEvidenceStore
from src.tools.models import ToolError, ToolRequest, ToolResult


class FakeInvoker:
    def __init__(self, result):
        self.result = result
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return self.result


class FakeVerifier:
    def __init__(self, status=ToolVerificationStatus.VERIFIED):
        self.status = status
        self.calls = []

    def verify(self, request, result):
        self.calls.append((request, result))
        return ToolExecutionVerification(
            request=request,
            result=result,
            status=self.status,
            evidence="independent verification observation",
            reason="verification boundary evaluated the concrete outcome",
        )


class ToolExecutionChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        auth_db = Path(self.temp.name) / "authorization.db"
        verification_db = Path(self.temp.name) / "verification.db"
        self.authorization_store = ToolAuthorizationEvidenceStore(auth_db)
        self.verification_store = ToolExecutionVerificationEvidenceStore(verification_db)
        self.policy = StaticToolAuthorizationPolicy(
            (
                ToolAuthorizationPolicyRule(
                    policy_id="ops-read",
                    scope="diagnostics",
                    allowed_capability_classes=("diagnostic",),
                    allowed_tools=("ping_host",),
                ),
            )
        )
        self.step = PlanStep(
            step_id="step-1",
            description="Ping a host",
            action="USE_TOOL",
            order=0,
            requires_confirmation=True,
            metadata={
                "tool_name": "ping_host",
                "arguments": {"host": "127.0.0.1"},
                "scope": "diagnostics",
                "capability_class": "diagnostic",
            },
        )

    def tearDown(self):
        self.temp.cleanup()

    def _chain(self, result=None, verifier=None):
        result = result or ToolResult(
            success=True,
            tool_name="ping_host",
            content={"reachable": True},
            invocation_id="step-1",
        )
        invoker = FakeInvoker(result)
        verifier = verifier or FakeVerifier()
        return (
            ToolExecutionChain(
                invoker=invoker,
                policy=self.policy,
                authorization_store=self.authorization_store,
                verifier=verifier,
                verification_store=self.verification_store,
            ),
            invoker,
            verifier,
        )

    def test_full_chain_persists_authorization_before_execution_and_verification_after(self):
        chain, invoker, verifier = self._chain()
        request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="step-1",
        )
        confirmation = ToolExecutionConfirmation(step_id="step-1", request=request)

        trace = chain.execute(self.step, confirmation)

        self.assertEqual(1, len(invoker.requests))
        self.assertEqual(1, len(verifier.calls))
        self.assertEqual(trace.request, verifier.calls[0][0])
        self.assertEqual(trace.request, invoker.requests[0])
        self.assertEqual(trace.authorization_evidence.evidence.authorized, True)
        self.assertEqual(trace.verification_evidence.verification, trace.verification)
        self.assertIsNotNone(self.authorization_store.get(trace.authorization_evidence.evidence_id))
        self.assertIsNotNone(self.verification_store.get(trace.verification_evidence.evidence_id))

    def test_denied_authorization_is_persisted_and_stops_chain_before_invocation(self):
        chain, invoker, verifier = self._chain()
        self.step = PlanStep(
            step_id="step-denied",
            description="Ping a host",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "ping_host",
                "arguments": {"host": "127.0.0.1"},
                "scope": "production",
                "capability_class": "diagnostic",
            },
        )

        with self.assertRaises(PermissionError):
            chain.execute(self.step)

        self.assertEqual([], invoker.requests)
        self.assertEqual([], verifier.calls)
        records = self.authorization_store.list_for_step("step-denied")
        self.assertEqual(1, len(records))
        self.assertFalse(records[0].evidence.authorized)
        self.assertEqual((), self.verification_store.all())

    def test_confirmation_failure_stops_before_execution_and_verification(self):
        chain, invoker, verifier = self._chain()
        request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="step-1",
        )

        with self.assertRaises(PermissionError):
            chain.execute(self.step, ToolExecutionConfirmation(
                step_id="step-1", request=request, confirmed=False
            ))

        self.assertEqual([], invoker.requests)
        self.assertEqual([], verifier.calls)
        self.assertEqual(1, len(self.authorization_store.list_for_step("step-1")))
        self.assertEqual((), self.verification_store.all())

    def test_failed_tool_result_still_reaches_verification_boundary(self):
        result = ToolResult(
            success=False,
            tool_name="ping_host",
            error=ToolError(code="timeout", message="host did not respond"),
            invocation_id="step-1",
        )
        chain, invoker, verifier = self._chain(result=result)
        request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="step-1",
        )
        confirmation = ToolExecutionConfirmation(step_id="step-1", request=request)

        trace = chain.execute(self.step, confirmation)

        self.assertFalse(trace.result.success)
        self.assertEqual(1, len(invoker.requests))
        self.assertEqual(1, len(verifier.calls))
        self.assertEqual(1, len(self.verification_store.all()))

    def test_unverified_outcome_is_persisted_without_becoming_verified(self):
        verifier = FakeVerifier(ToolVerificationStatus.UNVERIFIED)
        chain, _, _ = self._chain(verifier=verifier)
        request = ToolRequest(
            tool_name="ping_host",
            arguments={"host": "127.0.0.1"},
            metadata={"scope": "diagnostics", "capability_class": "diagnostic"},
            invocation_id="step-1",
        )
        confirmation = ToolExecutionConfirmation(step_id="step-1", request=request)

        trace = chain.execute(self.step, confirmation)

        self.assertIs(ToolVerificationStatus.UNVERIFIED, trace.verification.status)
        stored = self.verification_store.get(trace.verification_evidence.evidence_id)
        self.assertIsNotNone(stored)
        self.assertIs(ToolVerificationStatus.UNVERIFIED, stored.verification.status)


if __name__ == "__main__":
    unittest.main()
