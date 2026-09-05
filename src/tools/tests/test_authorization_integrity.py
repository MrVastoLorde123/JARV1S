from __future__ import annotations

import unittest

from src.tools.authorization import AuthorizationDecision, AuthorizationStatus
from src.tools.authorization_integrity import (
    AuthorizationIntegrityResult,
    AuthorizationIntegrityService,
)
from src.tools.models import ToolRequest
from src.tools.policy import PolicyDecision


class AuthorizationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuthorizationIntegrityService()
        self.request = ToolRequest(
            tool_name="echo",
            arguments={"message": "hello"},
            metadata={"source": "test"},
            invocation_id="inv-1",
        )
        self.decision = AuthorizationDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.ALLOW,
            confirmation_approved=None,
            status=AuthorizationStatus.GRANTED,
        )

    def test_attestation_is_valid_for_exact_request(self) -> None:
        result = self.service.attest(self.decision, self.request)
        self.assertTrue(result.valid)
        self.assertTrue(self.service.verify(result, self.decision, self.request))

    def test_changed_arguments_fail_integrity(self) -> None:
        result = self.service.attest(self.decision, self.request)
        changed = ToolRequest(
            tool_name="echo",
            arguments={"message": "changed"},
            metadata={"source": "test"},
            invocation_id="inv-1",
        )
        self.assertFalse(self.service.verify(result, self.decision, changed))

    def test_changed_metadata_fail_integrity(self) -> None:
        result = self.service.attest(self.decision, self.request)
        changed = ToolRequest(
            tool_name="echo",
            arguments={"message": "hello"},
            metadata={"source": "other"},
            invocation_id="inv-1",
        )
        self.assertFalse(self.service.verify(result, self.decision, changed))

    def test_changed_invocation_id_fails_integrity(self) -> None:
        result = self.service.attest(self.decision, self.request)
        changed = ToolRequest(
            tool_name="echo",
            arguments={"message": "hello"},
            metadata={"source": "test"},
            invocation_id="inv-2",
        )
        self.assertFalse(self.service.verify(result, self.decision, changed))

    def test_denied_decision_cannot_produce_valid_integrity(self) -> None:
        denied = AuthorizationDecision(
            authorization_id="auth-2",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.DENY,
            confirmation_approved=None,
            status=AuthorizationStatus.DENIED,
        )
        result = self.service.attest(denied, self.request)
        self.assertFalse(result.valid)
        self.assertFalse(self.service.verify(result, denied, self.request))

    def test_tampered_attestation_is_rejected(self) -> None:
        result = self.service.attest(self.decision, self.request)
        tampered = AuthorizationIntegrityResult(
            authorization_id=result.authorization_id,
            request_fingerprint="tampered",
            decision_fingerprint=result.decision_fingerprint,
            valid=True,
        )
        self.assertFalse(self.service.verify(tampered, self.decision, self.request))

    def test_context_is_non_executing(self) -> None:
        result = self.service.attest(self.decision, self.request)
        context = result.to_context()
        self.assertTrue(context["authorization_integrity_valid"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

    def test_invalid_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.attest(object(), self.request)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.service.attest(self.decision, object())  # type: ignore[arg-type]

    def test_result_requires_failure_reason_when_invalid(self) -> None:
        with self.assertRaises(ValueError):
            AuthorizationIntegrityResult(
                authorization_id="auth-1",
                request_fingerprint="req",
                decision_fingerprint="dec",
                valid=False,
            )


if __name__ == "__main__":
    unittest.main()
