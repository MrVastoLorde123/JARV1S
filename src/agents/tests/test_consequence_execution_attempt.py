import unittest

from src.agents.authority_handoff import AuthorityHandoffPolicy
from src.agents.claim_evidence import Claim
from src.agents.consequence_authorization import ConsequenceAuthorizationService
from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttemptService,
    ConsequenceExecutionAttemptStatus,
)
from src.agents.consequence_execution_preparation import ConsequenceExecutionPreparationService
from src.agents.consequence_gate import ConsequenceAction, ConsequenceDecision, ConsequenceKind, ConsequenceRequest
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.policy import DefaultPolicy


class RecordingExecutor:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def execute(self, handoff):
        self.calls.append(handoff)
        if self.error is not None:
            raise self.error
        return self.result


class M34ConsequenceExecutionAttemptTests(unittest.TestCase):
    def setUp(self):
        claim = Claim(
            task_id="task-34",
            actor="coding_agent",
            payload={"objective": "attempt prepared workflow"},
            provenance={"operation_id": "op-34"},
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
            evidence_refs=("evidence-34",),
            verification_refs=("verification-34",),
        )
        handoff = AuthorityHandoffPolicy().handoff(
            decision,
            authority_target="coding_confirmation",
            authority_context={"operation_id": "op-34"},
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
            arguments={"path": "example.txt", "content": "attempted"},
            metadata={
                "authority_handoff_id": handoff.handoff_id,
                "task_id": claim.task_id,
            },
            invocation_id="invocation-34",
        )
        authorization = ConsequenceAuthorizationService(
            ExplicitAuthorizationService(
                DefaultPolicy(),
                AutoApproveConfirmationProvider(),
            )
        ).authorize(
            handoff,
            self.definition,
            self.request,
            authorization_id="auth-34",
        )
        self.preparation = ConsequenceExecutionPreparationService().prepare(
            authorization,
            self.definition,
            self.request,
        )
        self.success_result = ToolResult(
            success=True,
            tool_name="write_file",
            content={"changed": True},
            invocation_id="invocation-34",
        )

    def test_prepared_consequence_attempts_through_existing_boundary(self):
        executor = RecordingExecutor(result=self.success_result)
        result = ConsequenceExecutionAttemptService(executor).attempt(self.preparation)

        self.assertEqual(result.status, ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED)
        self.assertTrue(result.attempted)
        self.assertTrue(result.completed)
        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(executor.calls[0].handoff_id, self.preparation.execution_handoff.handoff_id)
        self.assertEqual(result.execution_result, self.success_result)

    def test_full_provenance_survives_attempt(self):
        executor = RecordingExecutor(result=self.success_result)
        result = ConsequenceExecutionAttemptService(executor).attempt(self.preparation)

        self.assertEqual(result.preparation_id, self.preparation.preparation_id)
        self.assertEqual(result.authorization_id, self.preparation.authorization_id)
        self.assertEqual(result.handoff_id, self.preparation.handoff_id)
        self.assertEqual(result.claim_id, self.preparation.claim_id)
        self.assertEqual(result.task_id, self.preparation.task_id)
        self.assertEqual(result.consequence_id, self.preparation.consequence_id)
        self.assertEqual(result.evidence_refs, self.preparation.evidence_refs)
        self.assertEqual(result.verification_refs, self.preparation.verification_refs)
        self.assertEqual(result.execution_id, result.underlying_attempt.execution_id)

    def test_failed_executor_becomes_failed_attempt_data(self):
        executor = RecordingExecutor(error=RuntimeError("executor unavailable"))
        result = ConsequenceExecutionAttemptService(executor).attempt(self.preparation)

        self.assertEqual(result.status, ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED)
        self.assertTrue(result.attempted)
        self.assertFalse(result.completed)
        self.assertTrue(result.authorization_granted)
        self.assertIn("executor unavailable", result.reason)
        self.assertIsNone(result.execution_result)

    def test_preparation_failure_does_not_call_executor(self):
        executor = RecordingExecutor(result=self.success_result)
        blocked = self.preparation.__class__(
            preparation_id="blocked-preparation",
            authorization_id=self.preparation.authorization_id,
            handoff_id=self.preparation.handoff_id,
            claim_id=self.preparation.claim_id,
            task_id=self.preparation.task_id,
            consequence_id=self.preparation.consequence_id,
            tool_name=self.preparation.tool_name,
            invocation_id=self.preparation.invocation_id,
            status=self.preparation.status.BLOCKED,
            authorization_granted=True,
            evidence_refs=self.preparation.evidence_refs,
            verification_refs=self.preparation.verification_refs,
            integrity=self.preparation.integrity,
            sandbox_admission=self.preparation.sandbox_admission,
            execution_handoff=None,
            reason="sandbox admission blocked preparation",
        )
        result = ConsequenceExecutionAttemptService(executor).attempt(blocked)

        self.assertEqual(result.status, ConsequenceExecutionAttemptStatus.BLOCKED)
        self.assertFalse(result.attempted)
        self.assertIsNone(result.execution_id)
        self.assertEqual(len(executor.calls), 0)

    def test_attempt_is_not_new_authorization(self):
        executor = RecordingExecutor(result=self.success_result)
        result = ConsequenceExecutionAttemptService(executor).attempt(self.preparation)
        context = result.to_context()

        self.assertTrue(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["worker_assigned"])
        self.assertFalse(context["containment_active"])

    def test_executor_result_identity_is_enforced_by_existing_boundary(self):
        executor = RecordingExecutor(
            result=ToolResult(
                success=True,
                tool_name="delete_file",
                content={},
                invocation_id="invocation-34",
            )
        )
        result = ConsequenceExecutionAttemptService(executor).attempt(self.preparation)

        self.assertEqual(result.status, ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED)
        self.assertIn("tool identity", result.reason)

    def test_wrong_types_are_rejected(self):
        executor = RecordingExecutor(result=self.success_result)
        service = ConsequenceExecutionAttemptService(executor)
        with self.assertRaises(TypeError):
            service.attempt(object())


if __name__ == "__main__":
    unittest.main()
