import unittest

from src.agents.authority_handoff import AuthorityHandoffPolicy
from src.agents.claim_evidence import Claim
from src.agents.consequence_authorization import (
    ConsequenceAuthorizationService,
    ConsequenceAuthorizationStatus,
)
from src.agents.consequence_execution_preparation import (
    ConsequenceExecutionPreparationService,
    ConsequenceExecutionPreparationStatus,
)
from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision, ConsequenceKind, ConsequenceRequest
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest
from src.tools.policy import DefaultPolicy


class M33ConsequenceExecutionPreparationTests(unittest.TestCase):
    def setUp(self):
        claim = Claim(
            task_id="task-33",
            actor="coding_agent",
            payload={"objective": "prepare authorized workflow"},
            provenance={"operation_id": "op-33"},
        )
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
            metadata={"scope": "coding"},
        )
        decision = ConsequenceDecision(
            claim_id=claim.claim_id,
            task_id=claim.task_id,
            consequence=consequence,
            action=ConsequenceAction.ALLOW,
            reason="verified evidence",
            evidence_refs=("evidence-33",),
            verification_refs=("verification-33",),
        )
        self.handoff = AuthorityHandoffPolicy().handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-33"},
        )
        self.definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"sandbox_profile_id": "default"},
        )
        self.request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "prepared"},
            metadata={
                "authority_handoff_id": self.handoff.handoff_id,
                "task_id": claim.task_id,
            },
            invocation_id="invocation-33",
        )
        self.authorization = ConsequenceAuthorizationService(
            ExplicitAuthorizationService(
                DefaultPolicy(),
                AutoApproveConfirmationProvider(),
            )
        ).authorize(
            self.handoff,
            self.definition,
            self.request,
            authorization_id="auth-33",
        )
        self.service = ConsequenceExecutionPreparationService()

    def test_authorized_consequence_prepares_through_existing_boundaries(self):
        self.assertEqual(self.authorization.status, ConsequenceAuthorizationStatus.AUTHORIZED)
        result = self.service.prepare(self.authorization, self.definition, self.request)

        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.PREPARED)
        self.assertTrue(result.prepared)
        self.assertIsNotNone(result.integrity)
        self.assertTrue(result.integrity.valid)
        self.assertIsNotNone(result.sandbox_admission)
        self.assertTrue(result.sandbox_admission.admissible)
        self.assertIsNotNone(result.execution_handoff)

    def test_full_provenance_survives_preparation(self):
        result = self.service.prepare(self.authorization, self.definition, self.request)

        self.assertEqual(result.authorization_id, self.authorization.authorization_id)
        self.assertEqual(result.handoff_id, self.authorization.handoff_id)
        self.assertEqual(result.claim_id, self.authorization.claim_id)
        self.assertEqual(result.task_id, self.authorization.task_id)
        self.assertEqual(result.consequence_id, self.authorization.consequence_id)
        self.assertEqual(result.evidence_refs, self.authorization.evidence_refs)
        self.assertEqual(result.verification_refs, self.authorization.verification_refs)
        self.assertEqual(result.execution_handoff.authorization_id, self.authorization.authorization_id)
        self.assertEqual(result.execution_handoff.tool_name, self.request.tool_name)
        self.assertEqual(result.execution_handoff.invocation_id, self.request.invocation_id)

    def test_preparation_is_not_execution(self):
        result = self.service.prepare(self.authorization, self.definition, self.request)
        context = result.to_context()

        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["execution_started"])
        self.assertFalse(context["worker_assigned"])
        self.assertFalse(context["containment_active"])
        self.assertIsNone(result.execution_handoff.to_context().get("execution_started")) if False else self.assertFalse(
            result.execution_handoff.to_context()["execution_started"]
        )

    def test_denied_consequence_cannot_prepare(self):
        denied = ConsequenceDecision(
            **{
                **self.handoff.__dict__,
            }
        )
        # Rebuild the denied handoff from an explicit blocked consequence so
        # the M31 status is not READY_FOR_AUTHORITY.
        blocked_decision = ConsequenceDecision(
            claim_id=self.handoff.claim_id,
            task_id=self.handoff.task_id,
            consequence=self.handoff.consequence,
            action=ConsequenceAction.BLOCK,
            reason="blocked",
            evidence_refs=self.handoff.evidence_refs,
            verification_refs=self.handoff.verification_refs,
        )
        blocked_handoff = AuthorityHandoffPolicy().handoff(
            blocked_decision,
            authority_target="coding_confirmation",
        )
        denied_authorization = ConsequenceAuthorizationService(
            ExplicitAuthorizationService(
                DefaultPolicy(),
                AutoApproveConfirmationProvider(),
            )
        ).authorize(
            blocked_handoff,
            self.definition,
            self.request,
            authorization_id="auth-denied",
        )
        self.assertEqual(denied_authorization.status, ConsequenceAuthorizationStatus.DENIED)

        result = self.service.prepare(denied_authorization, self.definition, self.request)
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.BLOCKED)
        self.assertIsNone(result.execution_handoff)
        self.assertIn("authorization", result.reason)

    def test_definition_identity_must_match_request(self):
        wrong_definition = ToolDefinition(
            name="delete_file",
            description="delete a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        result = self.service.prepare(self.authorization, wrong_definition, self.request)
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.BLOCKED)
        self.assertIn("definition identity", result.reason)

    def test_request_identity_is_rechecked_against_underlying_authorization(self):
        mismatched_request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "other.txt"},
            metadata=self.request.metadata,
            invocation_id="other-invocation",
        )
        result = self.service.prepare(
            self.authorization,
            self.definition,
            mismatched_request,
        )
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.BLOCKED)
        self.assertIn("invocation", result.reason)

    def test_non_default_sandbox_profile_from_definition_is_used(self):
        from src.plugins.sandbox import SandboxProfile, SandboxProfileRegistry
        from src.tools.sandbox_admission import SandboxAdmissionService

        registry = SandboxProfileRegistry()
        registry.register(SandboxProfile(profile_id="coding"))
        definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            metadata={"sandbox_profile_id": "coding"},
        )
        service = ConsequenceExecutionPreparationService(
            sandbox_admission_service=SandboxAdmissionService(registry)
        )

        result = service.prepare(self.authorization, definition, self.request)
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.PREPARED)
        self.assertEqual(result.sandbox_admission.profile_id, "coding")

    def test_missing_sandbox_profile_blocks_preparation(self):
        definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            metadata={"sandbox_profile_id": "missing-profile"},
        )
        result = self.service.prepare(self.authorization, definition, self.request)
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.BLOCKED)
        self.assertIsNotNone(result.sandbox_admission)
        self.assertFalse(result.sandbox_admission.admissible)
        self.assertIn("sandbox profile", result.reason)

    def test_context_keeps_authorization_without_promoting_execution(self):
        result = self.service.prepare(self.authorization, self.definition, self.request)
        context = result.to_context()
        self.assertTrue(context["authorization_granted"])
        self.assertTrue(context["execution_prepared"])
        self.assertFalse(context["execution_started"])

    def test_wrong_types_are_rejected(self):
        with self.assertRaises(TypeError):
            self.service.prepare(object(), self.definition, self.request)
        with self.assertRaises(TypeError):
            self.service.prepare(self.authorization, object(), self.request)
        with self.assertRaises(TypeError):
            self.service.prepare(self.authorization, self.definition, object())


if __name__ == "__main__":
    unittest.main()
