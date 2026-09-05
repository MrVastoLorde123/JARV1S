from __future__ import annotations

import unittest

from src.tools.authorization import AuthorizationStatus, ExplicitAuthorizationService
from src.tools.confirmation import (
    AutoApproveConfirmationProvider,
    AutoDenyConfirmationProvider,
    ConfirmationResponse,
)
from src.tools.errors import (
    InvalidAuthorizationDecisionError,
    InvalidConfirmationResponseError,
    InvalidPolicyVerdictError,
)
from src.tools.models import RiskLevel, ToolRequest
from src.tools.policy import DefaultPolicy, PolicyDecision, PolicyVerdict
from src.tools.tests.support import (
    MalformedConfirmationProvider,
    MalformedPolicy,
    StubConfirmationProvider,
    allow_policy,
    confirmation_required_policy,
    deny_policy,
    make_definition,
)


class AuthorizationBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.definition = make_definition(name="echo")
        self.request = ToolRequest(tool_name="echo", arguments={"value": 1}, invocation_id="inv-1")

    def test_allow_becomes_explicit_authorization(self) -> None:
        service = ExplicitAuthorizationService(
            allow_policy(), AutoDenyConfirmationProvider()
        )

        result = service.authorize(
            self.definition,
            self.request,
            authorization_id="auth-1",
        )

        self.assertEqual(result.status, AuthorizationStatus.GRANTED)
        self.assertTrue(result.authorized)
        self.assertIsNone(result.confirmation_approved)
        self.assertEqual(result.authorization_id, "auth-1")

    def test_policy_deny_cannot_be_authorized(self) -> None:
        service = ExplicitAuthorizationService(
            deny_policy("blocked"), AutoApproveConfirmationProvider()
        )

        result = service.authorize(
            self.definition,
            self.request,
            authorization_id="auth-2",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)
        self.assertFalse(result.authorized)
        self.assertEqual(result.policy_decision, PolicyDecision.DENY)
        self.assertIsNone(result.confirmation_approved)
        self.assertIn("blocked", result.reason)

    def test_confirmation_approval_creates_authorization(self) -> None:
        service = ExplicitAuthorizationService(
            confirmation_required_policy(), AutoApproveConfirmationProvider()
        )

        result = service.authorize(
            self.definition,
            self.request,
            authorization_id="auth-3",
        )

        self.assertEqual(result.status, AuthorizationStatus.GRANTED)
        self.assertTrue(result.authorized)
        self.assertEqual(result.confirmation_approved, True)

    def test_confirmation_denial_prevents_authorization(self) -> None:
        service = ExplicitAuthorizationService(
            confirmation_required_policy(),
            StubConfirmationProvider(
                ConfirmationResponse(approved=False, reason="user denied")
            ),
        )

        result = service.authorize(
            self.definition,
            self.request,
            authorization_id="auth-4",
        )

        self.assertEqual(result.status, AuthorizationStatus.DENIED)
        self.assertFalse(result.authorized)
        self.assertEqual(result.confirmation_approved, False)
        self.assertIn("user denied", result.reason)

    def test_authorization_is_non_executing(self) -> None:
        service = ExplicitAuthorizationService(
            allow_policy(), AutoDenyConfirmationProvider()
        )

        result = service.authorize(
            self.definition,
            self.request,
            authorization_id="auth-5",
        )
        context = result.to_context()

        self.assertTrue(context["authorization_granted"])
        self.assertTrue(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

    def test_granted_decision_rejects_inconsistent_fields(self) -> None:
        with self.assertRaises(InvalidAuthorizationDecisionError):
            from src.tools.authorization import AuthorizationDecision

            AuthorizationDecision(
                authorization_id="auth-6",
                tool_name="echo",
                invocation_id="inv-1",
                policy_decision=PolicyDecision.REQUIRE_CONFIRMATION,
                confirmation_approved=False,
                status=AuthorizationStatus.GRANTED,
            )

    def test_malformed_policy_is_rejected(self) -> None:
        service = ExplicitAuthorizationService(
            MalformedPolicy(), AutoDenyConfirmationProvider()
        )

        with self.assertRaises(InvalidPolicyVerdictError):
            service.authorize(
                self.definition,
                self.request,
                authorization_id="auth-7",
            )

    def test_malformed_confirmation_is_rejected(self) -> None:
        service = ExplicitAuthorizationService(
            confirmation_required_policy(), MalformedConfirmationProvider()
        )

        with self.assertRaises(InvalidConfirmationResponseError):
            service.authorize(
                self.definition,
                self.request,
                authorization_id="auth-8",
            )

    def test_default_policy_requires_confirmation_for_high_risk(self) -> None:
        definition = make_definition(name="delete", risk_level=RiskLevel.HIGH)
        request = ToolRequest(tool_name="delete")
        service = ExplicitAuthorizationService(
            DefaultPolicy(), AutoDenyConfirmationProvider()
        )

        result = service.authorize(definition, request, authorization_id="auth-9")

        self.assertEqual(result.status, AuthorizationStatus.DENIED)
        self.assertEqual(result.policy_decision, PolicyDecision.REQUIRE_CONFIRMATION)
        self.assertEqual(result.confirmation_approved, False)


if __name__ == "__main__":
    unittest.main()
