"""CS2 red-team coverage for the canonical execution authority boundary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization, require_authorization
from src.core.tool_authorization_evidence_recording import ToolAuthorizationEvidenceRecorder
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.tools.authorization import AuthorizationStatus
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.policy import DefaultPolicy, PolicyDecision
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class _RecorderToolHandler:
    def __init__(self, name: str = "echo", risk_level: RiskLevel = RiskLevel.LOW) -> None:
        self.calls = 0
        self._definition = ToolDefinition(
            name=name,
            description="test tool",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
            risk_level=risk_level,
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        self.calls += 1
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content="executed",
            invocation_id=request.invocation_id,
        )


class DeploymentClosureCS2ExecutionAuthorityTests(unittest.TestCase):
    def _step(self, *, step_id: str = "step-1", request: ToolRequest | None = None) -> PlanStep:
        request = request or ToolRequest(
            tool_name="echo",
            arguments={"value": "hello"},
            invocation_id="invoke-1",
        )
        return PlanStep(
            step_id=step_id,
            description="execute echo",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": request.tool_name,
                "arguments": dict(request.arguments),
                "invocation_id": request.invocation_id,
            },
        )

    def _authorization(
        self,
        step: PlanStep,
        *,
        authorized: bool = True,
        request: ToolRequest | None = None,
    ) -> ToolExecutionAuthorization:
        request = request or ToolRequest(
            tool_name="echo",
            arguments={"value": "hello"},
            invocation_id="invoke-1",
        )
        return ToolExecutionAuthorization(
            step_id=step.step_id,
            request=request,
            authorized=authorized,
            policy_id="test-policy",
            reason="test authorization" if authorized else "test denial",
        )

    def test_no_authorization_is_rejected(self) -> None:
        step = self._step()
        request = ToolExecutionAuthorization(
            step_id=step.step_id,
            request=ToolRequest(tool_name="echo", invocation_id="invoke-1"),
            authorized=False,
            policy_id="test-policy",
            reason="denied",
        )
        with self.assertRaises(PermissionError):
            require_authorization(step, self._step_request(step), request)

    def test_wrong_step_is_rejected(self) -> None:
        original = self._step(step_id="step-1")
        wrong = self._step(step_id="step-2")
        authorization = self._authorization(original)
        with self.assertRaises(PermissionError):
            require_authorization(wrong, self._step_request(wrong), authorization)

    def test_wrong_request_is_rejected(self) -> None:
        step = self._step()
        authorized_request = self._step_request(step)
        wrong_request = ToolRequest(
            tool_name="echo",
            arguments={"value": "different"},
            invocation_id="invoke-1",
        )
        authorization = self._authorization(step, request=authorized_request)
        with self.assertRaises(PermissionError):
            require_authorization(step, wrong_request, authorization)

    def test_denied_authorization_is_rejected(self) -> None:
        step = self._step()
        request = self._step_request(step)
        authorization = self._authorization(step, authorized=False, request=request)
        with self.assertRaises(PermissionError):
            require_authorization(step, request, authorization)

    def test_exact_granted_authorization_is_admitted(self) -> None:
        step = self._step()
        request = self._step_request(step)
        authorization = self._authorization(step, request=request)
        require_authorization(step, request, authorization)

    def test_policy_denial_is_durable_and_never_executes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ToolAuthorizationEvidenceStore(Path(tmp) / "jarvis.db")
            recorder = ToolAuthorizationEvidenceRecorder(store)
            handler = _RecorderToolHandler()
            registry = ToolRegistry()
            registry.register(handler)
            gate = PolicyGate(
                registry,
                ToolService(registry),
                DefaultPolicy(blocked_tools={"echo"}),
                authorization_recorder=recorder,
            )

            result = gate.invoke(
                ToolRequest(
                    tool_name="echo",
                    invocation_id="invoke-denied",
                )
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "policy_denied")
            self.assertEqual(handler.calls, 0)
            evidence = store.list_for_step("invoke-denied")
            self.assertEqual(len(evidence), 1)
            self.assertFalse(evidence[0].evidence.authorized)

    def test_missing_durable_evidence_fails_closed_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handler = _RecorderToolHandler()
            registry = ToolRegistry()
            registry.register(handler)

            def failing_recorder(request, definition, decision):
                raise RuntimeError("store unavailable")

            gate = PolicyGate(
                registry,
                ToolService(registry),
                DefaultPolicy(),
                authorization_recorder=failing_recorder,
            )

            result = gate.invoke(
                ToolRequest(
                    tool_name="echo",
                    invocation_id="invoke-no-evidence",
                )
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "authorization_evidence_failed")
            self.assertEqual(handler.calls, 0)

    def test_valid_authorization_admits_execution_and_produces_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ToolAuthorizationEvidenceStore(Path(tmp) / "jarvis.db")
            recorder = ToolAuthorizationEvidenceRecorder(store)
            handler = _RecorderToolHandler()
            registry = ToolRegistry()
            registry.register(handler)
            gate = PolicyGate(
                registry,
                ToolService(registry),
                DefaultPolicy(),
                authorization_recorder=recorder,
            )

            result = gate.invoke(
                ToolRequest(
                    tool_name="echo",
                    arguments={"value": "hello"},
                    invocation_id="invoke-valid",
                )
            )

            self.assertTrue(result.success)
            self.assertEqual(result.content, "executed")
            self.assertEqual(handler.calls, 1)
            evidence = store.list_for_step("invoke-valid")
            self.assertEqual(len(evidence), 1)
            self.assertTrue(evidence[0].evidence.authorized)

    @staticmethod
    def _step_request(step: PlanStep) -> ToolRequest:
        return ToolRequest(
            tool_name=step.metadata["tool_name"],
            arguments=dict(step.metadata["arguments"]),
            invocation_id=step.metadata["invocation_id"],
        )


if __name__ == "__main__":
    unittest.main()
