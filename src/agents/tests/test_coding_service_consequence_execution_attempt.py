import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttemptService,
    ConsequenceExecutionAttemptStatus,
)
from src.tools.models import ToolResult


class RecordingExecutor:
    def __init__(self, result=None):
        self.result = result
        self.calls = []

    def execute(self, handoff):
        self.calls.append(handoff)
        return self.result


class M34CodingServiceConsequenceExecutionAttemptTests(unittest.TestCase):
    def setUp(self):
        self.service = CodingAgentService(planner=object(), worker=object())

    def test_service_requires_explicit_attempt_binding(self):
        with self.assertRaises(RuntimeError):
            self.service.attempt_prepared_consequence(object())

    def test_service_binds_executor_and_attempts_prepared_consequence(self):
        executor = RecordingExecutor(
            result=ToolResult(
                success=True,
                tool_name="write_file",
                content={"changed": True},
                invocation_id="invocation-34-service",
            )
        )
        preparation = _build_preparation_for_service()
        self.service.bind_consequence_execution_attempt(executor)
        result = self.service.attempt_prepared_consequence(preparation)

        self.assertEqual(result.status, ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED)
        self.assertEqual(len(executor.calls), 1)

    def test_service_accepts_injected_attempt_service(self):
        preparation = _build_preparation_for_service()
        executor = RecordingExecutor(
            result=ToolResult(
                success=True,
                tool_name="write_file",
                content={"changed": True},
                invocation_id="invocation-34-service",
            )
        )
        attempt_service = ConsequenceExecutionAttemptService(executor)
        self.service.bind_consequence_execution_attempt(attempt_service=attempt_service)
        result = self.service.attempt_prepared_consequence(preparation)

        self.assertTrue(result.completed)
        self.assertEqual(len(executor.calls), 1)

    def test_service_rejects_ambiguous_binding(self):
        executor = RecordingExecutor()
        with self.assertRaises(ValueError):
            self.service.bind_consequence_execution_attempt(
                executor,
                attempt_service=ConsequenceExecutionAttemptService(executor),
            )


def _build_preparation_for_service():
    from src.agents.authority_handoff import AuthorityHandoffPolicy
    from src.agents.claim_evidence import Claim
    from src.agents.consequence_authorization import ConsequenceAuthorizationService
    from src.agents.consequence_execution_preparation import ConsequenceExecutionPreparationService
    from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision, ConsequenceKind, ConsequenceRequest
    from src.tools.authorization import ExplicitAuthorizationService
    from src.tools.confirmation import AutoApproveConfirmationProvider
    from src.tools.models import RiskLevel, ToolDefinition, ToolRequest
    from src.tools.policy import DefaultPolicy

    claim = Claim(
        task_id="task-34-service",
        actor="coding_agent",
        payload={"objective": "attempt prepared workflow"},
        provenance={"operation_id": "op-34-service"},
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
        reason="verified",
        evidence_refs=("evidence-34-service",),
        verification_refs=("verification-34-service",),
    )
    handoff = AuthorityHandoffPolicy().handoff(
        decision,
        authority_target="coding_confirmation",
    )
    definition = ToolDefinition(
        name="write_file",
        description="write a file",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        risk_level=RiskLevel.LOW,
        metadata={"sandbox_profile_id": "default"},
    )
    request = ToolRequest(
        tool_name="write_file",
        arguments={"path": "example.txt", "content": "attempted"},
        metadata={
            "authority_handoff_id": handoff.handoff_id,
            "task_id": claim.task_id,
        },
        invocation_id="invocation-34-service",
    )
    authorization = ConsequenceAuthorizationService(
        ExplicitAuthorizationService(
            DefaultPolicy(),
            AutoApproveConfirmationProvider(),
        )
    ).authorize(
        handoff,
        definition,
        request,
        authorization_id="auth-34-service",
    )
    return ConsequenceExecutionPreparationService().prepare(
        authorization,
        definition,
        request,
    )


if __name__ == "__main__":
    unittest.main()
