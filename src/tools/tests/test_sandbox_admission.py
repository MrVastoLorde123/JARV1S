from __future__ import annotations

import unittest

from src.plugins.sandbox import SandboxProfile, SandboxProfileRegistry
from src.tools.authorization import AuthorizationDecision, AuthorizationStatus
from src.tools.authorization_integrity import AuthorizationIntegrityResult
from src.tools.errors import InvalidRequestError
from src.tools.models import ToolRequest
from src.tools.policy import PolicyDecision
from src.tools.sandbox_admission import (
    SandboxAdmissionDecision,
    SandboxAdmissionIntegrationError,
    SandboxAdmissionService,
    SandboxAdmissionStatus,
)


class SandboxAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SandboxProfileRegistry()
        self.registry.register(SandboxProfile(profile_id="default"))
        self.service = SandboxAdmissionService(self.registry)
        self.request = ToolRequest(tool_name="echo", arguments={"x": 1}, invocation_id="inv-1")
        self.authorization = AuthorizationDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.ALLOW,
            confirmation_approved=None,
            status=AuthorizationStatus.GRANTED,
        )
        self.integrity = AuthorizationIntegrityResult(
            authorization_id="auth-1",
            request_fingerprint="request-fp",
            decision_fingerprint="decision-fp",
            valid=True,
            reason=None,
        )

    def test_exact_authorized_integrity_verified_request_is_admissible(self) -> None:
        result = self.service.admit(self.authorization, self.integrity, self.request)

        self.assertTrue(result.admissible)
        self.assertEqual(result.profile_id, "default")

    def test_admission_does_not_grant_authority_or_execution(self) -> None:
        result = self.service.admit(self.authorization, self.integrity, self.request)
        context = result.to_context()

        self.assertTrue(context["sandbox_admitted"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["containment_active"])

    def test_denied_authorization_never_becomes_admissible(self) -> None:
        denied = AuthorizationDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.DENY,
            confirmation_approved=None,
            status=AuthorizationStatus.DENIED,
            reason="blocked",
        )

        result = self.service.admit(denied, self.integrity, self.request)

        self.assertFalse(result.admissible)
        self.assertIn("authorization is not granted", result.reason or "")

    def test_invalid_integrity_blocks_admission(self) -> None:
        invalid = AuthorizationIntegrityResult(
            authorization_id="auth-1",
            request_fingerprint="request-fp",
            decision_fingerprint="decision-fp",
            valid=False,
            reason="tampered",
        )

        result = self.service.admit(self.authorization, invalid, self.request)

        self.assertFalse(result.admissible)
        self.assertIn("authorization integrity is invalid", result.reason or "")

    def test_authorization_request_identity_mismatch_blocks(self) -> None:
        mismatched = ToolRequest(tool_name="other", arguments={"x": 1}, invocation_id="inv-1")
        result = self.service.admit(self.authorization, self.integrity, mismatched)

        self.assertFalse(result.admissible)
        self.assertIn("authorization tool identity does not match request", result.reason or "")

    def test_custom_declared_profile_is_used(self) -> None:
        self.registry.register(SandboxProfile(profile_id="restricted"))
        result = self.service.admit(
            self.authorization,
            self.integrity,
            self.request,
            profile_id="restricted",
        )

        self.assertTrue(result.admissible)
        self.assertEqual(result.profile_id, "restricted")

    def test_unregistered_profile_blocks_admission(self) -> None:
        result = self.service.admit(
            self.authorization,
            self.integrity,
            self.request,
            profile_id="missing",
        )

        self.assertFalse(result.admissible)
        self.assertIn("is not registered", result.reason or "")

    def test_rejected_decision_requires_reason(self) -> None:
        with self.assertRaises(SandboxAdmissionIntegrationError):
            SandboxAdmissionDecision(
                authorization_id="auth-1",
                tool_name="echo",
                invocation_id="inv-1",
                profile_id="default",
                status=SandboxAdmissionStatus.REJECTED,
            )

    def test_invalid_request_type_is_rejected(self) -> None:
        with self.assertRaises(InvalidRequestError):
            self.service.admit(  # type: ignore[arg-type]
                self.authorization,
                self.integrity,
                {"tool_name": "echo"},
            )


if __name__ == "__main__":
    unittest.main()
