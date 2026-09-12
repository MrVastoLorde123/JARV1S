import unittest

from src.agents.authority_handoff import AuthorityHandoffPolicy
from src.agents.claim_evidence import Claim
from src.agents.coding_service import CodingAgentService
from src.agents.consequence_authorization import (
    ConsequenceAuthorizationService,
    ConsequenceAuthorizationStatus,
)
from src.agents.consequence_execution_preparation import (
    ConsequenceExecutionPreparationService,
    ConsequenceExecutionPreparationStatus,
)
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceDecision,
    ConsequenceKind,
    ConsequenceRequest,
)
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest
from src.tools.policy import DefaultPolicy


class M33CodingServiceConsequenceExecutionPreparationTests(unittest.TestCase):
    def setUp(self):
        self.service = CodingAgentService(planner=object(), worker=object())
        self.authorization_service = ExplicitAuthorizationService(
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
        )
        claim = Claim(
            task_id="task-service-33",
            actor="coding_agent",
            payload={"objective": "prepare workflow"},
            provenance={"operation_id": "op-service-33"},
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
            evidence_refs=("evidence-service-33",),
            verification_refs=("verification-service-33",),
        )
        self.handoff = AuthorityHandoffPolicy().handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-service-33"},
        )
        self.definition = ToolDefinition(
            name="write_file",
            description="write a file",
            version="1.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            metadata={"sandbox_profile_id": "default"},
        )
        self.request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "prepared"},
            metadata={
                "authority_handoff_id": self.handoff.handoff_id,
                "task_id": claim.task_id,
            },
            invocation_id="invocation-service-33",
        )

    def authorized(self):
        return ConsequenceAuthorizationService(self.authorization_service).authorize(
            self.handoff,
            self.definition,
            self.request,
            authorization_id="auth-service-33",
        )

    def test_service_requires_m33_binding(self):
        authorization = self.authorized()
        self.assertEqual(authorization.status, ConsequenceAuthorizationStatus.AUTHORIZED)
        with self.assertRaises(RuntimeError):
            self.service.prepare_authorized_consequence(
                authorization,
                self.definition,
                self.request,
            )

    def test_service_prepares_authorized_consequence_without_execution(self):
        authorization = self.authorized()
        self.service.bind_consequence_execution_preparation()

        result = self.service.prepare_authorized_consequence(
            authorization,
            self.definition,
            self.request,
        )
        self.assertEqual(result.status, ConsequenceExecutionPreparationStatus.PREPARED)
        self.assertTrue(result.prepared)
        self.assertEqual(result.authorization_id, authorization.authorization_id)
        self.assertFalse(result.to_context()["execution_started"])
        self.assertFalse(result.to_context()["worker_assigned"])

    def test_service_accepts_explicit_m33_service_binding(self):
        authorization = self.authorized()
        preparation = ConsequenceExecutionPreparationService()
        self.service.bind_consequence_execution_preparation(preparation)

        result = self.service.prepare_authorized_consequence(
            authorization,
            self.definition,
            self.request,
        )
        self.assertIsInstance(result, type(preparation.prepare(
            authorization,
            self.definition,
            self.request,
        )))


if __name__ == "__main__":
    unittest.main()
