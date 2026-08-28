from __future__ import annotations

import unittest

from src.tools.errors import ToolLayerError
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy, PolicyDecision, PolicyVerdict
from src.tools.tests.support import make_definition


class TestPolicyVerdict(unittest.TestCase):
    def test_valid_verdict(self) -> None:
        verdict = PolicyVerdict(decision=PolicyDecision.ALLOW)
        self.assertIsNone(verdict.reason)

    def test_rejects_non_decision(self) -> None:
        with self.assertRaises(ToolLayerError):
            PolicyVerdict(decision="allow")  # type: ignore[arg-type]

    def test_rejects_non_string_reason(self) -> None:
        with self.assertRaises(ToolLayerError):
            PolicyVerdict(decision=PolicyDecision.ALLOW, reason=123)  # type: ignore[arg-type]


class TestDefaultPolicy(unittest.TestCase):
    def test_low_risk_no_confirmation_is_allowed(self) -> None:
        policy = DefaultPolicy()
        definition = make_definition(name="echo", risk_level=RiskLevel.LOW)
        request = ToolRequest(tool_name="echo")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.ALLOW)

    def test_medium_risk_no_confirmation_is_allowed_by_default(self) -> None:
        policy = DefaultPolicy()
        definition = make_definition(name="echo", risk_level=RiskLevel.MEDIUM)
        request = ToolRequest(tool_name="echo")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.ALLOW)

    def test_high_and_critical_risk_require_confirmation(self) -> None:
        for risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            with self.subTest(risk_level=risk_level):
                policy = DefaultPolicy()
                definition = make_definition(name="delete_everything", risk_level=risk_level)
                request = ToolRequest(tool_name="delete_everything")

                verdict = policy.evaluate(definition, request)

                self.assertEqual(verdict.decision, PolicyDecision.REQUIRE_CONFIRMATION)
                self.assertIsNotNone(verdict.reason)

    def test_explicit_requires_confirmation_flag_is_honored_even_at_low_risk(self) -> None:
        policy = DefaultPolicy()
        definition = make_definition(
            name="send_email", risk_level=RiskLevel.LOW, requires_confirmation=True
        )
        request = ToolRequest(tool_name="send_email")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.REQUIRE_CONFIRMATION)

    def test_blocked_tool_is_denied_even_at_low_risk(self) -> None:
        policy = DefaultPolicy(blocked_tools={"echo"})
        definition = make_definition(name="echo", risk_level=RiskLevel.LOW)
        request = ToolRequest(tool_name="echo")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.DENY)
        self.assertIsNotNone(verdict.reason)

    def test_blocked_tools_normalized_for_matching(self) -> None:
        policy = DefaultPolicy(blocked_tools={"  Echo  "})
        definition = make_definition(name="ECHO")
        request = ToolRequest(tool_name="ECHO")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.DENY)

    def test_deny_takes_precedence_over_confirmation(self) -> None:
        policy = DefaultPolicy(blocked_tools={"delete_everything"})
        definition = make_definition(
            name="delete_everything", risk_level=RiskLevel.CRITICAL, requires_confirmation=True
        )
        request = ToolRequest(tool_name="delete_everything")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.DENY)

    def test_custom_confirmation_risk_levels(self) -> None:
        policy = DefaultPolicy(confirmation_risk_levels={RiskLevel.MEDIUM})
        definition = make_definition(name="echo", risk_level=RiskLevel.MEDIUM)
        request = ToolRequest(tool_name="echo")

        verdict = policy.evaluate(definition, request)

        self.assertEqual(verdict.decision, PolicyDecision.REQUIRE_CONFIRMATION)

    def test_is_side_effect_free_and_stateless_across_calls(self) -> None:
        policy = DefaultPolicy()
        definition = make_definition(name="echo")
        request = ToolRequest(tool_name="echo")

        first = policy.evaluate(definition, request)
        second = policy.evaluate(definition, request)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
