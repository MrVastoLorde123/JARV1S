from __future__ import annotations

import unittest

from src.tools.authorization import AuthorizationStatus
from src.tools.confirmation import AutoApproveConfirmationProvider, AutoDenyConfirmationProvider
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.tests.support import EchoHandler, allow_policy, confirmation_required_policy, deny_policy


class PolicyGateAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.service = ToolService(self.registry)

    def make_gate(self, policy, confirmation_provider=None) -> PolicyGate:
        return PolicyGate(self.registry, self.service, policy, confirmation_provider)

    def test_authorize_allows_without_execution(self) -> None:
        handler = EchoHandler(name="echo")
        self.registry.register(handler)
        gate = self.make_gate(allow_policy())

        decision = gate.authorize(
            ToolRequest(tool_name="echo", arguments={"x": 1}),
            authorization_id="auth-1",
        )

        self.assertEqual(decision.status, AuthorizationStatus.GRANTED)
        self.assertTrue(decision.authorized)
        self.assertEqual(decision.authorization_id, "auth-1")

    def test_authorize_denies_without_execution(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(deny_policy("blocked"))

        decision = gate.authorize(
            ToolRequest(tool_name="echo"),
            authorization_id="auth-2",
        )

        self.assertEqual(decision.status, AuthorizationStatus.DENIED)
        self.assertFalse(decision.authorized)
        self.assertIn("blocked", decision.reason)

    def test_invoke_requires_authorization_before_service(self) -> None:
        handler = EchoHandler(name="echo")
        self.registry.register(handler)
        gate = self.make_gate(deny_policy())

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "policy_denied")

    def test_invoke_executes_after_explicit_authorization(self) -> None:
        handler = EchoHandler(name="echo")
        self.registry.register(handler)
        gate = self.make_gate(allow_policy())

        result = gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))

        self.assertTrue(result.success)
        self.assertEqual(result.content, {"x": 1})

    def test_invoke_executes_only_after_confirmed_authorization(self) -> None:
        handler = EchoHandler(
            name="echo",
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
        )
        self.registry.register(handler)
        gate = self.make_gate(
            confirmation_required_policy(), AutoApproveConfirmationProvider()
        )

        decision = gate.authorize(
            ToolRequest(tool_name="echo"),
            authorization_id="auth-confirmed",
        )
        self.assertEqual(decision.status, AuthorizationStatus.GRANTED)
        self.assertTrue(decision.confirmation_approved)

        result = gate.invoke(ToolRequest(tool_name="echo"))
        self.assertTrue(result.success)

    def test_confirmation_denial_never_reaches_service(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(
            confirmation_required_policy(), AutoDenyConfirmationProvider()
        )

        decision = gate.authorize(
            ToolRequest(tool_name="echo"),
            authorization_id="auth-denied",
        )
        self.assertFalse(decision.authorized)

        result = gate.invoke(ToolRequest(tool_name="echo"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")


if __name__ == "__main__":
    unittest.main()
