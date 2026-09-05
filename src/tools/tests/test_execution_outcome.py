from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.authorization import AuthorizationDecision, AuthorizationStatus
from src.tools.authorization_integrity import AuthorizationIntegrityResult
from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
from src.tools.execution_outcome import (
    ExecutionOutcome,
    ExecutionOutcomeError,
    ExecutionOutcomeService,
    ExecutionOutcomeStatus,
)
from src.tools.execution_preparation import ExecutionHandoff
from src.tools.models import ToolError, ToolResult
from src.tools.policy import PolicyDecision


class ExecutionOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ExecutionOutcomeService()
        self.handoff = ExecutionHandoff(
            handoff_id="handoff-1",
            authorization_id="auth-1",
            request_fingerprint="request-fp",
            decision_fingerprint="decision-fp",
            sandbox_profile_id="default",
            tool_name="echo",
            invocation_id="inv-1",
            arguments={"x": 1},
        )

    def execution_id(self) -> str:
        return self._attempt().execution_id

    def _attempt(self) -> ExecutionAttemptResult:
        return ExecutionAttemptResult(
            execution_id="exec-1",
            handoff_id="handoff-1",
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionAttemptStatus.COMPLETED,
            result=ToolResult(
                success=True,
                tool_name="echo",
                content={"x": 1},
                invocation_id="inv-1",
            ),
        )

    def _valid_attempt(self) -> ExecutionAttemptResult:
        attempt = self._attempt()
        expected = self.service._expected_execution_id(self.handoff)
        return ExecutionAttemptResult(
            execution_id=expected,
            handoff_id=attempt.handoff_id,
            tool_name=attempt.tool_name,
            invocation_id=attempt.invocation_id,
            status=attempt.status,
            result=attempt.result,
        )

    def test_successful_attempt_produces_succeeded_outcome(self) -> None:
        outcome = self.service.interpret(self._valid_attempt(), self.handoff)

        self.assertTrue(outcome.succeeded)
        self.assertEqual(outcome.status, ExecutionOutcomeStatus.SUCCEEDED)
        self.assertEqual(outcome.result.content, {"x": 1})

    def test_tool_failure_is_distinguished_from_executor_failure(self) -> None:
        attempt = ExecutionAttemptResult(
            execution_id=self.service._expected_execution_id(self.handoff),
            handoff_id="handoff-1",
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionAttemptStatus.FAILED,
            result=ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_execution_error", message="bad args"),
                invocation_id="inv-1",
            ),
            reason="bad args",
        )

        outcome = self.service.interpret(attempt, self.handoff)

        self.assertEqual(outcome.status, ExecutionOutcomeStatus.TOOL_FAILED)
        self.assertIn("bad args", outcome.reason or "")

    def test_executor_failure_has_no_tool_result(self) -> None:
        attempt = ExecutionAttemptResult(
            execution_id=self.service._expected_execution_id(self.handoff),
            handoff_id="handoff-1",
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionAttemptStatus.FAILED,
            result=None,
            reason="worker unavailable",
        )

        outcome = self.service.interpret(attempt, self.handoff)

        self.assertEqual(outcome.status, ExecutionOutcomeStatus.EXECUTOR_FAILED)
        self.assertIsNone(outcome.result)
        self.assertIn("worker unavailable", outcome.reason or "")

    def test_wrong_execution_id_is_rejected(self) -> None:
        attempt = self._valid_attempt()
        tampered = ExecutionAttemptResult(
            execution_id="exec-tampered",
            handoff_id=attempt.handoff_id,
            tool_name=attempt.tool_name,
            invocation_id=attempt.invocation_id,
            status=attempt.status,
            result=attempt.result,
        )

        with self.assertRaisesRegex(ExecutionOutcomeError, "execution identity"):
            self.service.interpret(tampered, self.handoff)

    def test_wrong_handoff_id_is_rejected(self) -> None:
        attempt = self._valid_attempt()
        tampered = ExecutionAttemptResult(
            execution_id=attempt.execution_id,
            handoff_id="handoff-other",
            tool_name=attempt.tool_name,
            invocation_id=attempt.invocation_id,
            status=attempt.status,
            result=attempt.result,
        )

        with self.assertRaisesRegex(ExecutionOutcomeError, "handoff identity"):
            self.service.interpret(tampered, self.handoff)

    def test_wrong_tool_identity_is_rejected(self) -> None:
        attempt = self._valid_attempt()
        tampered = ExecutionAttemptResult(
            execution_id=attempt.execution_id,
            handoff_id=attempt.handoff_id,
            tool_name="other",
            invocation_id=attempt.invocation_id,
            status=attempt.status,
            result=attempt.result,
        )

        with self.assertRaisesRegex(ExecutionOutcomeError, "tool identity"):
            self.service.interpret(tampered, self.handoff)

    def test_completed_attempt_cannot_contain_failed_result(self) -> None:
        invalid = ExecutionAttemptResult(
            execution_id=self.service._expected_execution_id(self.handoff),
            handoff_id="handoff-1",
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionAttemptStatus.COMPLETED,
            result=ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_execution_error", message="boom"),
                invocation_id="inv-1",
            ),
        )

        with self.assertRaisesRegex(ExecutionOutcomeError, "completed execution attempt"):
            self.service.interpret(invalid, self.handoff)

    def test_failed_attempt_cannot_contain_success_result(self) -> None:
        invalid = ExecutionAttemptResult(
            execution_id=self.service._expected_execution_id(self.handoff),
            handoff_id="handoff-1",
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionAttemptStatus.FAILED,
            result=ToolResult(success=True, tool_name="echo", invocation_id="inv-1"),
            reason="worker failed",
        )

        with self.assertRaisesRegex(ExecutionOutcomeError, "failed execution attempt"):
            self.service.interpret(invalid, self.handoff)

    def test_outcome_is_immutable(self) -> None:
        outcome = self.service.interpret(self._valid_attempt(), self.handoff)

        with self.assertRaises(FrozenInstanceError):
            outcome.status = ExecutionOutcomeStatus.TOOL_FAILED  # type: ignore[misc]

    def test_outcome_context_does_not_grant_or_learn(self) -> None:
        context = self.service.interpret(self._valid_attempt(), self.handoff).to_context()

        self.assertTrue(context["execution_succeeded"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_malformed_inputs_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret({}, self.handoff)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.service.interpret(self._valid_attempt(), {})  # type: ignore[arg-type]

    def test_outcome_contract_rejects_missing_reason_for_executor_failure(self) -> None:
        with self.assertRaises(ExecutionOutcomeError):
            ExecutionOutcome(
                execution_id="exec-1",
                handoff_id="handoff-1",
                tool_name="echo",
                invocation_id="inv-1",
                status=ExecutionOutcomeStatus.EXECUTOR_FAILED,
            )


if __name__ == "__main__":
    unittest.main()
