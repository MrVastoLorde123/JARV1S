import unittest

from src.agents.authority_handoff import AuthorityHandoffPolicy
from src.agents.claim_evidence import Claim
from src.agents.coding_service import CodingAgentService
from src.agents.consequence_authorization import ConsequenceAuthorizationStatus
from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision, ConsequenceKind, ConsequenceRequest
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest
from src.tools.policy import DefaultPolicy


class M32CodingServiceConsequenceAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.service = CodingAgentService(planner=object(), worker=object())
        self.authorization = ExplicitAuthorizationService(
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
        )
        claim = Claim(
            task_id="task-service-32",
            actor="coding_agent",
            payload={"objective": "authorize workflow"},
            provenance={"operation_id": "op-service-32"},
        )
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
        )
        decision = ConsequenceDecision(
            claim_id=claim.claim_id,
            task_id=claim.task_id,
            consequence=consequence,
            action=ConsequenceAction.ALLOW,
            reason="verified",
            evidence_refs=("evidence-service-32",),
            verification_refs=("verification-service-32",),
        )
        self.handoff = AuthorityHandoffPolicy().handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-service-32"},
        )
        self.definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
        )
        self.request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "ok"},
            metadata={
                "authority_handoff_id": self.handoff.handoff_id,
                "task_id": claim.task_id,
            },
            invocation_id="invocation-service-32",
        )

    def test_service_requires_explicit_authorization_binding(self):
        with self.assertRaises(RuntimeError):
            self.service.authorize_consequence(
                self.handoff,
                self.definition,
                self.request,
                authorization_id="auth-service-32",
            )

    def test_service_authorizes_through_existing_m22_8_boundary(self):
        self.service.bind_consequence_authorization(
            self.authorization,
            authority_target="coding_confirmation",
        )
        result = self.service.authorize_consequence(
            self.handoff,
            self.definition,
            self.request,
            authorization_id="auth-service-32",
        )
        self.assertEqual(result.status, ConsequenceAuthorizationStatus.AUTHORIZED)
        self.assertTrue(result.authorized)
        self.assertEqual(result.handoff_id, self.handoff.handoff_id)
        self.assertEqual(result.evidence_refs, self.handoff.evidence_refs)

    def test_service_does_not_execute_from_authorization(self):
        self.service.bind_consequence_authorization(self.authorization)
        result = self.service.authorize_consequence(
            self.handoff,
            self.definition,
            self.request,
            authorization_id="auth-inert-service-32",
        )
        self.assertTrue(result.authorized)
        self.assertFalse(result.to_context()["execution_requested"])


if __name__ == "__main__":
    unittest.main()
