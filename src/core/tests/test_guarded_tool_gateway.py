from __future__ import annotations

import unittest

from src.core.guarded_tool_gateway import GuardedToolCapabilityGateway
from src.tools.confirmation import AutoApproveConfirmationProvider, ConfirmationResponse
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from src.tools.policy import DefaultPolicy, Policy, PolicyDecision, PolicyVerdict
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class FakeHandler:
    def __init__(self, definition: ToolDefinition) -> None:
        self._definition = definition
        self.requests: list[ToolRequest] = []

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        self.requests.append(request)
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content="executed",
            invocation_id=request.invocation_id,
        )


class DenyPolicy:
    def evaluate(self, definition: ToolDefinition, request: ToolRequest) -> PolicyVerdict:
        return PolicyVerdict(PolicyDecision.DENY, reason="blocked")


class RequireConfirmationPolicy:
    def evaluate(self, definition: ToolDefinition, request: ToolRequest) -> PolicyVerdict:
        return PolicyVerdict(PolicyDecision.REQUIRE_CONFIRMATION, reason="confirm")


class DenyConfirmationProvider:
    def confirm(self, definition: ToolDefinition, request: ToolRequest) -> ConfirmationResponse:
        return ConfirmationResponse(False, reason="user denied")


class M26_5GuardedToolGatewayTests(unittest.TestCase):
    def make_definition(self, *, confirmation: bool = False) -> ToolDefinition:
        return ToolDefinition(
            name="read_file",
            description="Read a file",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
            risk_level=RiskLevel.MEDIUM,
            requires_confirmation=confirmation,
        )

    def make_gate(self, policy: Policy, confirmation_provider=None):
        registry = ToolRegistry()
        handler = FakeHandler(self.make_definition())
        registry.register(handler)
        service = ToolService(registry)
        gate = PolicyGate(
            registry,
            service,
            policy,
            confirmation_provider=confirmation_provider,
        )
        return gate, handler

    def test_requires_exact_policy_gate(self):
        with self.assertRaises(TypeError):
            GuardedToolCapabilityGateway(object())

    def test_definitions_are_forwarded_from_gate(self):
        gate, _ = self.make_gate(DefaultPolicy())
        gateway = GuardedToolCapabilityGateway(gate)
        definitions = gateway.list_definitions()
        self.assertEqual(len(definitions), 1)
        self.assertIsInstance(definitions[0], ToolDefinition)

    def test_invoke_requires_exact_tool_request(self):
        gate, _ = self.make_gate(DefaultPolicy())
        gateway = GuardedToolCapabilityGateway(gate)
        with self.assertRaises(TypeError):
            gateway.invoke(object())

    def test_allowed_request_crosses_gate_and_reaches_executor(self):
        gate, handler = self.make_gate(DefaultPolicy())
        gateway = GuardedToolCapabilityGateway(gate)
        request = ToolRequest(tool_name="read_file", invocation_id="inv-1")
        result = gateway.invoke(request)
        self.assertIsInstance(result, ToolResult)
        self.assertTrue(result.success)
        self.assertEqual(handler.requests, [request])
        self.assertIs(handler.requests[0], request)

    def test_policy_denial_never_reaches_executor(self):
        gate, handler = self.make_gate(DenyPolicy())
        gateway = GuardedToolCapabilityGateway(gate)
        result = gateway.invoke(ToolRequest(tool_name="read_file", invocation_id="inv-2"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "policy_denied")
        self.assertEqual(handler.requests, [])

    def test_confirmation_denial_never_reaches_executor(self):
        gate, handler = self.make_gate(RequireConfirmationPolicy(), DenyConfirmationProvider())
        gateway = GuardedToolCapabilityGateway(gate)
        result = gateway.invoke(ToolRequest(tool_name="read_file", invocation_id="inv-3"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")
        self.assertEqual(handler.requests, [])

    def test_confirmation_approval_reaches_executor_only_through_gate(self):
        gate, handler = self.make_gate(
            RequireConfirmationPolicy(),
            AutoApproveConfirmationProvider(),
        )
        gateway = GuardedToolCapabilityGateway(gate)
        request = ToolRequest(tool_name="read_file", invocation_id="inv-4")
        result = gateway.invoke(request)
        self.assertTrue(result.success)
        self.assertEqual(handler.requests, [request])

    def test_result_identity_is_preserved_as_data(self):
        class RecordingExecutor:
            def __init__(self):
                self.requests = []
                self.result = ToolResult(
                    success=False,
                    tool_name="read_file",
                    error=ToolError(code="x", message="failure"),
                    invocation_id="inv-5",
                )

            def execute(self, handoff):
                self.requests.append(handoff)
                return self.result

        registry = ToolRegistry()
        registry.register(FakeHandler(self.make_definition()))
        service = ToolService(registry)
        executor = RecordingExecutor()
        gate = PolicyGate(registry, service, DefaultPolicy(), executor=executor)
        gateway = GuardedToolCapabilityGateway(gate)
        result = gateway.invoke(ToolRequest(tool_name="read_file", invocation_id="inv-5"))
        self.assertFalse(result.success)
        self.assertEqual(result.invocation_id, "inv-5")

    def test_declared_gate_is_not_a_second_authority_surface(self):
        gate, _ = self.make_gate(DefaultPolicy())
        gateway = GuardedToolCapabilityGateway(gate)
        self.assertFalse(gateway.bypasses_authorization)
        self.assertFalse(gateway.bypasses_confirmation)
        self.assertFalse(gateway.executes_directly)
        self.assertFalse(gateway.mutates_state)
        self.assertFalse(gateway.persists_state)
        self.assertFalse(gateway.establishes_truth)
        self.assertFalse(gateway.establishes_certainty)


if __name__ == "__main__":
    unittest.main()
