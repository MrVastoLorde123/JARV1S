import unittest

from src.agents.authority_handoff import (
    AuthorityHandoffPolicy,
    AuthorityHandoffStatus,
)
from src.agents.claim_evidence import Claim
from src.agents.consequence_authorization import (
    ConsequenceAuthorizationDecision,
    ConsequenceAuthorizationService,
    ConsequenceAuthorizationStatus,
)
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceDecision,
    ConsequenceKind,
    ConsequenceRequest,
)
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.confirmation import AutoApproveConfirmationProvider, AutoDenyConfirmationProvider
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest
from src.tools.policy import DefaultPolicy


class M32ConsequenceAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim(
            task_id="task-32",
            actor="coding_agent",
            payload={"objective": "authorize verified workflow"},
            provenance={"operation_id": "op-32"},
        )
        self.consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
            metadata={"scope": "coding"},
        )
        self.decision = ConsequenceDecision(
            claim_id=self.claim.claim_id,
            task_id=self.claim.task_id,
            consequence=self.consequence,
            action=ConsequenceAction.ALLOW,
            reason="verified evidence",
            evidence_refs=("evidence-32",),
            verification_refs=("verification-32",),
        )
        self.handoff = AuthorityHandoffPolicy().handoff(
            self.decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-32"},
        )
        self.definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
        )

    def request(self, **metadata):
        return ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "ok"},
            metadata={
                "authority_handoff_id": self.handoff.handoff_id,
                "task_id": self.claim.task_id,
                **metadata,
            },
            invocation_id="invocation-32",
        )

    def service(self, confirmation=None, policy=None):
        return ConsequenceAuthorizationService(
            ExplicitAuthorizationService(
                policy or DefaultPolicy(),
                confirmation or AutoApproveConfirmationProvider(),
            )
        )

    def test_ready_handoff_is_authorized_by_existing_m22_8_service(self):
        result = self.service().authorize(
            self.handoff,
            self.definition,
            self.request(),
            authorization_id="auth-32",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.AUTHORIZED)
        self.assertTrue(result.authorized)
        self.assertIsNotNone(result.underlying_decision)
        self.assertTrue(result.underlying_decision.authorized)

    def test_provenance_survives_into_authorization(self):
        result = self.service().authorize(
            self.handoff,
            self.definition,
            self.request(),
            authorization_id="auth-32",
        )
        self.assertEqual(result.authorization_id, "auth-32")
        self.assertEqual(result.handoff_id, self.handoff.handoff_id)
        self.assertEqual(result.claim_id, self.claim.claim_id)
        self.assertEqual(result.task_id, self.claim.task_id)
        self.assertEqual(result.consequence_id, self.consequence.consequence_id)
        self.assertEqual(result.evidence_refs, self.handoff.evidence_refs)
        self.assertEqual(result.verification_refs, self.handoff.verification_refs)

    def test_blocked_handoff_is_denied_without_entering_authorization(self):
        blocked = ConsequenceDecision(
            **{**self.decision.__dict__, "action": ConsequenceAction.BLOCK}
        )
        handoff = AuthorityHandoffPolicy().handoff(
            blocked,
            authority_target="coding_confirmation",
        )
        result = self.service().authorize(
            handoff,
            self.definition,
            self.request(),
            authorization_id="auth-blocked",
        )
        self.assertEqual(handoff.status, AuthorityHandoffStatus.BLOCKED)
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNone(result.underlying_decision)

    def test_review_handoff_is_denied_without_entering_authorization(self):
        review = ConsequenceDecision(
            **{**self.decision.__dict__, "action": ConsequenceAction.REQUIRE_REVIEW}
        )
        handoff = AuthorityHandoffPolicy().handoff(
            review,
            authority_target="coding_confirmation",
        )
        result = self.service().authorize(
            handoff,
            self.definition,
            self.request(),
            authorization_id="auth-review",
        )
        self.assertEqual(handoff.status, AuthorityHandoffStatus.REQUIRE_REVIEW)
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNone(result.underlying_decision)

    def test_wrong_authority_target_is_denied(self):
        handoff = AuthorityHandoffPolicy().handoff(
            self.decision,
            authority_target="other_authority",
        )
        result = self.service().authorize(
            handoff,
            self.definition,
            self.request(),
            authorization_id="auth-target",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIn("target", result.reason)

    def test_mismatched_handoff_binding_is_denied(self):
        request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "ok"},
            metadata={"authority_handoff_id": "wrong", "task_id": self.claim.task_id},
            invocation_id="invocation-32",
        )
        result = self.service().authorize(
            self.handoff,
            self.definition,
            request,
            authorization_id="auth-mismatch",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNone(result.underlying_decision)

    def test_mismatched_task_binding_is_denied(self):
        request = self.request(task_id="other-task")
        result = self.service().authorize(
            self.handoff,
            self.definition,
            request,
            authorization_id="auth-task",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNone(result.underlying_decision)

    def test_policy_denial_is_preserved(self):
        policy = DefaultPolicy(blocked_tools={"write_file"})
        result = self.service(policy=policy).authorize(
            self.handoff,
            self.definition,
            self.request(),
            authorization_id="auth-policy",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNotNone(result.underlying_decision)
        self.assertFalse(result.underlying_decision.authorized)

    def test_confirmation_denial_is_preserved(self):
        definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
        )
        result = self.service(confirmation=AutoDenyConfirmationProvider()).authorize(
            self.handoff,
            definition,
            self.request(),
            authorization_id="auth-confirmation",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.DENIED)
        self.assertIsNotNone(result.underlying_decision)
        self.assertFalse(result.underlying_decision.authorized)
        self.assertFalse(result.underlying_decision.confirmation_approved)

    def test_authorization_is_not_execution(self):
        result = self.service().authorize(
            self.handoff,
            self.definition,
            self.request(),
            authorization_id="auth-inert",
        )
        self.assertTrue(result.authorized)
        self.assertEqual(result.to_context()["execution_requested"], False)

    def test_wrong_types_are_rejected(self):
        service = self.service()
        with self.assertRaises(TypeError):
            service.authorize(object(), self.definition, self.request(), authorization_id="a")
        with self.assertRaises(TypeError):
            service.authorize(self.handoff, object(), self.request(), authorization_id="a")
        with self.assertRaises(TypeError):
            service.authorize(self.handoff, self.definition, object(), authorization_id="a")

    def test_decision_contract_rejects_authorized_without_underlying_authorization(self):
        with self.assertRaises(ValueError):
            ConsequenceAuthorizationDecision(
                authorization_id="a",
                handoff_id="h",
                claim_id="c",
                task_id="t",
                consequence_id="x",
                tool_name="write_file",
                invocation_id="i",
                status=ConsequenceAuthorizationStatus.AUTHORIZED,
                underlying_decision=None,
                evidence_refs=(),
                verification_refs=(),
            )


if __name__ == "__main__":
    unittest.main()
