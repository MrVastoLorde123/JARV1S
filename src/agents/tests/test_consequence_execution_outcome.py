import unittest
from dataclasses import FrozenInstanceError

from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttempt,
    ConsequenceExecutionAttemptStatus,
)
from src.agents.consequence_execution_outcome import (
    ConsequenceExecutionOutcome,
    ConsequenceExecutionOutcomeService,
    ConsequenceExecutionOutcomeStatus,
)
from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
from src.tools.models import ToolError, ToolRequest, ToolResult
from src.tools.outcome import ExternalObservation, ExternalVerification, ExternalVerificationState, ToolOutcomeService


class M35ConsequenceExecutionOutcomeTests(unittest.TestCase):
    def _attempt(self, status, result=None, execution_id="execution-35", reason=None):
        underlying = None
        if status is not ConsequenceExecutionAttemptStatus.BLOCKED:
            underlying = ExecutionAttemptResult(
                execution_id=execution_id,
                handoff_id="handoff-35",
                tool_name="write_file",
                invocation_id="invocation-35",
                status=(ExecutionAttemptStatus.COMPLETED if status is ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED else ExecutionAttemptStatus.FAILED),
                result=result,
                reason=reason,
            )
        return ConsequenceExecutionAttempt(
            attempt_id="attempt-35",
            execution_id=None if status is ConsequenceExecutionAttemptStatus.BLOCKED else execution_id,
            preparation_id="prep-35",
            authorization_id="auth-35",
            handoff_id="handoff-35",
            claim_id="claim-35",
            task_id="task-35",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invocation-35",
            status=status,
            authorization_granted=True,
            evidence_refs=("evidence-35",),
            verification_refs=("verification-35",),
            execution_result=result,
            underlying_attempt=underlying,
            reason=reason if status is not ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED else None,
        )

    def test_success_attempt_becomes_success_outcome(self):
        result = ToolResult(success=True, tool_name="write_file", content={"changed": True}, invocation_id="invocation-35")
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED, result=result)
        )
        self.assertEqual(outcome.status, ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS)
        self.assertTrue(outcome.completed)
        self.assertTrue(outcome.successful)
        self.assertEqual(outcome.execution_result.content["changed"], True)

    def test_successful_execution_is_unverified_by_default(self):
        result = ToolResult(
            success=True,
            tool_name="write_file",
            content={"changed": True},
            invocation_id="invocation-35",
        )
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED, result=result)
        )
        self.assertEqual(
            outcome.verification_state,
            ExternalVerificationState.UNVERIFIED,
        )
        self.assertFalse(outcome.to_context()["externally_verified"])

    def test_explicit_verified_tool_outcome_promotes_execution_outcome_only(self):
        result = ToolResult(
            success=True,
            tool_name="write_file",
            content={"changed": True},
            invocation_id="invocation-verified",
        )
        attempt = self._attempt(
            ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED,
            result=result,
        )
        request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "example.txt", "content": "ok"},
            invocation_id="invocation-verified",
        )
        raw = ToolOutcomeService.classify(request, result)
        observed = ToolOutcomeService.observe(
            raw,
            ExternalObservation(
                observation_id="observation-verified",
                source="independent_reader",
                subject_ref=raw.target_ref,
                payload={"changed": True},
                observed_at="2026-09-19T01:00:00+00:00",
            ),
        )
        verified = ToolOutcomeService.verify(
            observed,
            ExternalVerification(
                verification_id="verification-verified",
                observation_id="observation-verified",
                verifier="independent_reader_check",
                passed=True,
            ),
        )

        outcome = ConsequenceExecutionOutcomeService().evaluate(
            attempt,
            verified,
        )

        self.assertEqual(
            outcome.verification_state,
            ExternalVerificationState.VERIFIED,
        )
        self.assertTrue(outcome.to_context()["externally_verified"])


    def test_failed_attempt_becomes_failure_outcome(self):
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(
                ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED,
                reason="executor unavailable",
            )
        )
        self.assertEqual(outcome.status, ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE)
        self.assertTrue(outcome.completed)
        self.assertFalse(outcome.successful)
        self.assertIn("executor unavailable", outcome.reason or "")

    def test_blocked_attempt_becomes_not_executed(self):
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(ConsequenceExecutionAttemptStatus.BLOCKED, reason="preparation blocked")
        )
        self.assertEqual(outcome.status, ConsequenceExecutionOutcomeStatus.NOT_EXECUTED)
        self.assertFalse(outcome.completed)
        self.assertFalse(outcome.successful)
        self.assertIsNone(outcome.execution_id)
        self.assertIsNone(outcome.execution_result)

    def test_full_provenance_is_preserved(self):
        attempt = self._attempt(
            ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED,
            result=ToolResult(success=True, tool_name="write_file", invocation_id="invocation-35"),
        )
        outcome = ConsequenceExecutionOutcomeService().evaluate(attempt)
        for field in ("attempt_id", "preparation_id", "authorization_id", "handoff_id", "claim_id", "task_id", "consequence_id", "tool_name", "invocation_id", "evidence_refs", "verification_refs"):
            self.assertEqual(getattr(outcome, field), getattr(attempt, field))

    def test_outcome_is_immutable(self):
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(ConsequenceExecutionAttemptStatus.BLOCKED, reason="blocked")
        )
        with self.assertRaises(FrozenInstanceError):
            outcome.reason = "tampered"  # type: ignore[misc]

    def test_context_does_not_promote_outcome_into_authority_or_learning(self):
        outcome = ConsequenceExecutionOutcomeService().evaluate(
            self._attempt(
                ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED,
                result=ToolResult(success=True, tool_name="write_file", invocation_id="invocation-35"),
            )
        )
        context = outcome.to_context()
        self.assertTrue(context["execution_outcome_observed"])
        self.assertTrue(context["authorization_granted"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["learning_write_requested"])

    def test_outcome_id_is_deterministic(self):
        attempt = self._attempt(
            ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED,
            result=ToolResult(success=True, tool_name="write_file", invocation_id="invocation-35"),
        )
        service = ConsequenceExecutionOutcomeService()
        self.assertEqual(service.evaluate(attempt).outcome_id, service.evaluate(attempt).outcome_id)

    def test_wrong_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceExecutionOutcomeService().evaluate(object())

    def test_successful_status_requires_success_result(self):
        with self.assertRaises(ValueError):
            ConsequenceExecutionOutcome(
                outcome_id="o", attempt_id="a", execution_id="e", preparation_id="p",
                authorization_id="auth", handoff_id="h", claim_id="c", task_id="t",
                consequence_id="x", tool_name="write_file", invocation_id="i",
                status=ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
                authorization_granted=True, evidence_refs=(), verification_refs=(),
                execution_result=ToolResult(
                    success=False, tool_name="write_file",
                    error=ToolError(code="failed", message="no"), invocation_id="i"
                ),
            )


if __name__ == "__main__":
    unittest.main()
