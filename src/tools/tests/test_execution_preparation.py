from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.authorization import AuthorizationDecision, AuthorizationStatus
from src.tools.authorization_integrity import AuthorizationIntegrityResult
from src.tools.execution_preparation import ExecutionHandoff, ExecutionPreparationError, ExecutionPreparationService
from src.tools.models import ToolRequest
from src.tools.policy import PolicyDecision
from src.tools.sandbox_admission import SandboxAdmissionDecision, SandboxAdmissionStatus


class ExecutionPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ExecutionPreparationService()
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
        )
        self.admission = SandboxAdmissionDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            profile_id="default",
            status=SandboxAdmissionStatus.ADMISSIBLE,
        )

    def prepare(self) -> ExecutionHandoff:
        return self.service.prepare(
            self.authorization,
            self.integrity,
            self.admission,
            self.request,
        )

    def test_exact_upstream_evidence_produces_handoff(self) -> None:
        handoff = self.prepare()

        self.assertEqual(handoff.authorization_id, "auth-1")
        self.assertEqual(handoff.request_fingerprint, "request-fp")
        self.assertEqual(handoff.decision_fingerprint, "decision-fp")
        self.assertEqual(handoff.sandbox_profile_id, "default")
        self.assertEqual(handoff.tool_name, "echo")
        self.assertEqual(handoff.arguments, {"x": 1})
        self.assertTrue(handoff.handoff_id.startswith("handoff-"))

    def test_handoff_is_immutable(self) -> None:
        handoff = self.prepare()

        with self.assertRaises(FrozenInstanceError):
            handoff.arguments = {}  # type: ignore[misc]

    def test_handoff_context_is_non_executing(self) -> None:
        context = self.prepare().to_context()

        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["worker_assigned"])
        self.assertFalse(context["containment_active"])

    def test_denied_authorization_cannot_be_prepared(self) -> None:
        denied = AuthorizationDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.DENY,
            confirmation_approved=None,
            status=AuthorizationStatus.DENIED,
            reason="blocked",
        )

        with self.assertRaisesRegex(ExecutionPreparationError, "authorization is not granted"):
            self.service.prepare(denied, self.integrity, self.admission, self.request)

    def test_invalid_integrity_cannot_be_prepared(self) -> None:
        invalid = AuthorizationIntegrityResult(
            authorization_id="auth-1",
            request_fingerprint="request-fp",
            decision_fingerprint="decision-fp",
            valid=False,
            reason="tampered",
        )

        with self.assertRaisesRegex(ExecutionPreparationError, "authorization integrity is invalid"):
            self.service.prepare(self.authorization, invalid, self.admission, self.request)

    def test_failed_admission_cannot_be_prepared(self) -> None:
        rejected = SandboxAdmissionDecision(
            authorization_id="auth-1",
            tool_name="echo",
            invocation_id="inv-1",
            profile_id="default",
            status=SandboxAdmissionStatus.REJECTED,
            reason="sandbox rejected",
        )

        with self.assertRaisesRegex(ExecutionPreparationError, "sandbox admission is not admissible"):
            self.service.prepare(self.authorization, self.integrity, rejected, self.request)

    def test_identity_mismatch_is_rejected(self) -> None:
        mismatched = ToolRequest(tool_name="other", arguments={"x": 1}, invocation_id="inv-1")

        with self.assertRaisesRegex(ExecutionPreparationError, "authorization tool identity"):
            self.service.prepare(self.authorization, self.integrity, self.admission, mismatched)

    def test_upstream_authorization_identity_mismatch_is_rejected(self) -> None:
        mismatched = AuthorizationDecision(
            authorization_id="auth-other",
            tool_name="echo",
            invocation_id="inv-1",
            policy_decision=PolicyDecision.ALLOW,
            confirmation_approved=None,
            status=AuthorizationStatus.GRANTED,
        )

        with self.assertRaisesRegex(ExecutionPreparationError, "integrity authorization identity"):
            self.service.prepare(mismatched, self.integrity, self.admission, self.request)

    def test_malformed_inputs_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.prepare(self.authorization, self.integrity, self.admission, {"tool_name": "echo"})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
