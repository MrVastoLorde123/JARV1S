import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttempt,
    ConsequenceExecutionAttemptStatus,
)
from src.agents.consequence_execution_outcome import ConsequenceExecutionOutcomeStatus
from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
from src.tools.models import ToolResult


class M35CodingServiceConsequenceExecutionOutcomeTests(unittest.TestCase):
    def _attempt(self, status, result=None, reason=None):
        underlying = None
        if status is not ConsequenceExecutionAttemptStatus.BLOCKED:
            underlying = ExecutionAttemptResult(
                execution_id="execution-service-35",
                handoff_id="handoff-service-35",
                tool_name="write_file",
                invocation_id="invocation-service-35",
                status=(ExecutionAttemptStatus.COMPLETED if status is ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED else ExecutionAttemptStatus.FAILED),
                result=result,
                reason=reason,
            )
        return ConsequenceExecutionAttempt(
            attempt_id="attempt-service-35",
            execution_id=None if status is ConsequenceExecutionAttemptStatus.BLOCKED else "execution-service-35",
            preparation_id="prep-service-35",
            authorization_id="auth-service-35",
            handoff_id="handoff-service-35",
            claim_id="claim-service-35",
            task_id="task-service-35",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invocation-service-35",
            status=status,
            authorization_granted=True,
            evidence_refs=("evidence-service-35",),
            verification_refs=("verification-service-35",),
            execution_result=result,
            underlying_attempt=underlying,
            reason=reason if status is not ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED else None,
        )

    def test_service_requires_explicit_outcome_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.evaluate_execution_outcome(self._attempt(ConsequenceExecutionAttemptStatus.BLOCKED, reason="blocked"))

    def test_service_evaluates_attempt_through_bound_outcome_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_outcome()
        result = service.evaluate_execution_outcome(
            self._attempt(
                ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED,
                result=ToolResult(success=True, tool_name="write_file", invocation_id="invocation-service-35"),
            )
        )
        self.assertEqual(result.status, ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS)

    def test_service_accepts_injected_outcome_service(self):
        from src.agents.consequence_execution_outcome import ConsequenceExecutionOutcomeService
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_outcome(ConsequenceExecutionOutcomeService())
        result = service.evaluate_execution_outcome(
            self._attempt(
                ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED,
                reason="executor unavailable",
            )
        )
        self.assertEqual(result.status, ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE)

    def test_outcome_evaluation_does_not_retry_or_execute(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_outcome()
        result = service.evaluate_execution_outcome(
            self._attempt(
                ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED,
                reason="executor unavailable",
            )
        )
        self.assertFalse(result.to_context()["retry_requested"])
        self.assertFalse(result.to_context()["learning_write_requested"])


if __name__ == "__main__":
    unittest.main()
