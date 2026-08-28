from __future__ import annotations

import unittest

from src.tools.confirmation import (
    AutoApproveConfirmationProvider,
    AutoDenyConfirmationProvider,
    ConfirmationResponse,
)
from src.tools.errors import (
    InvalidConfirmationResponseError,
    InvalidPolicyVerdictError,
    InvalidRequestError,
    UnknownToolError,
)
from src.tools.gate import PolicyGate
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.tests.support import (
    EchoHandler,
    MalformedConfirmationProvider,
    MalformedPolicy,
    StubConfirmationProvider,
    allow_policy,
    confirmation_required_policy,
    deny_policy,
)


class GateTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.service = ToolService(self.registry)

    def make_gate(self, policy, confirmation_provider=None) -> PolicyGate:
        return PolicyGate(self.registry, self.service, policy, confirmation_provider)


class TestAllow(GateTestCase):
    def test_allowed_request_reaches_the_handler(self) -> None:
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.LOW))
        gate = self.make_gate(allow_policy())

        result = gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))

        self.assertTrue(result.success)
        self.assertEqual(result.content, {"x": 1})

    def test_default_policy_allows_low_risk_tool_without_confirmation_provider(self) -> None:
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.LOW))
        gate = PolicyGate(self.registry, self.service, DefaultPolicy())

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertTrue(result.success)


class TestDeny(GateTestCase):
    def test_denied_request_never_reaches_the_handler(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(deny_policy("no reason to run this"))

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.code, "policy_denied")
        self.assertIn("no reason to run this", result.error.message)

    def test_deny_does_not_raise(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(deny_policy())

        # Should not raise -- denial is an expected outcome, not an exception.
        gate.invoke(ToolRequest(tool_name="echo"))


class TestConfirmation(GateTestCase):
    def test_require_confirmation_with_no_provider_defaults_to_deny(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(confirmation_required_policy())

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")

    def test_require_confirmation_with_explicit_deny_provider(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(confirmation_required_policy(), AutoDenyConfirmationProvider())

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")

    def test_require_confirmation_approved_reaches_the_handler(self) -> None:
        self.registry.register(EchoHandler(name="echo", requires_confirmation=True))
        gate = self.make_gate(confirmation_required_policy(), AutoApproveConfirmationProvider())

        result = gate.invoke(ToolRequest(tool_name="echo", arguments={"x": 1}))

        self.assertTrue(result.success)
        self.assertEqual(result.content, {"x": 1})

    def test_confirmation_denial_reason_is_propagated(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        provider = StubConfirmationProvider(
            ConfirmationResponse(approved=False, reason="user said no")
        )
        gate = self.make_gate(confirmation_required_policy(), provider)

        result = gate.invoke(ToolRequest(tool_name="echo"))

        self.assertIn("user said no", result.error.message)


class TestDefaultPolicyIntegration(GateTestCase):
    def test_high_risk_tool_requires_confirmation_end_to_end(self) -> None:
        self.registry.register(EchoHandler(name="delete_everything", risk_level=RiskLevel.HIGH))
        gate = PolicyGate(
            self.registry, self.service, DefaultPolicy(), AutoApproveConfirmationProvider()
        )

        result = gate.invoke(ToolRequest(tool_name="delete_everything"))

        self.assertTrue(result.success)

    def test_high_risk_tool_denied_confirmation_end_to_end(self) -> None:
        self.registry.register(EchoHandler(name="delete_everything", risk_level=RiskLevel.HIGH))
        gate = PolicyGate(self.registry, self.service, DefaultPolicy())

        result = gate.invoke(ToolRequest(tool_name="delete_everything"))

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")


class TestStructuralErrors(GateTestCase):
    def test_invalid_request_raises(self) -> None:
        gate = self.make_gate(allow_policy())
        with self.assertRaises(InvalidRequestError):
            gate.invoke({"tool_name": "echo"})  # type: ignore[arg-type]

    def test_unknown_tool_raises(self) -> None:
        gate = self.make_gate(allow_policy())
        with self.assertRaises(UnknownToolError):
            gate.invoke(ToolRequest(tool_name="does-not-exist"))

    def test_malformed_policy_verdict_raises(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(MalformedPolicy())

        with self.assertRaises(InvalidPolicyVerdictError):
            gate.invoke(ToolRequest(tool_name="echo"))

    def test_malformed_confirmation_response_raises(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        gate = self.make_gate(confirmation_required_policy(), MalformedConfirmationProvider())

        with self.assertRaises(InvalidConfirmationResponseError):
            gate.invoke(ToolRequest(tool_name="echo"))


class TestServiceIsolation(GateTestCase):
    def test_tool_service_unaware_of_policy(self) -> None:
        # A tool that would be denied by policy still runs fine when
        # ToolService is invoked directly -- proving ToolService has
        # no policy awareness baked in, and that the boundary lives
        # entirely in PolicyGate.
        self.registry.register(EchoHandler(name="echo", risk_level=RiskLevel.CRITICAL))
        result = self.service.invoke(ToolRequest(tool_name="echo"))
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
