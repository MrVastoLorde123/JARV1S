from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.execution_attempt import (
    ExecutionAttemptError,
    ExecutionAttemptResult,
    ExecutionAttemptService,
    ExecutionAttemptStatus,
)
from src.tools.execution_preparation import ExecutionHandoff
from src.tools.models import ToolError, ToolResult


class StubExecutor:
    def __init__(self, result: ToolResult | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls = 0
        self.last_handoff = None

    def execute(self, handoff: ExecutionHandoff) -> ToolResult:
        self.calls += 1
        self.last_handoff = handoff
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


class ExecutionAttemptTests(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_exact_handoff_produces_completed_attempt(self) -> None:
        tool_result = ToolResult(
            success=True,
            tool_name="echo",
            content={"x": 1},
            invocation_id="inv-1",
        )
        executor = StubExecutor(result=tool_result)
        outcome = ExecutionAttemptService(executor).attempt(self.handoff)

        self.assertTrue(outcome.completed)
        self.assertEqual(outcome.status, ExecutionAttemptStatus.COMPLETED)
        self.assertEqual(outcome.handoff_id, "handoff-1")
        self.assertEqual(outcome.tool_name, "echo")
        self.assertEqual(outcome.result, tool_result)
        self.assertEqual(executor.calls, 1)

    def test_failed_tool_result_is_not_successful_completion(self) -> None:
        tool_result = ToolResult(
            success=False,
            tool_name="echo",
            error=ToolError(code="tool_execution_error", message="boom"),
            invocation_id="inv-1",
        )
        outcome = ExecutionAttemptService(StubExecutor(result=tool_result)).attempt(self.handoff)

        self.assertFalse(outcome.completed)
        self.assertEqual(outcome.status, ExecutionAttemptStatus.FAILED)
        self.assertIn("boom", outcome.reason or "")

    def test_executor_exception_becomes_failed_attempt(self) -> None:
        outcome = ExecutionAttemptService(StubExecutor(error=RuntimeError("worker failed"))).attempt(
            self.handoff
        )

        self.assertFalse(outcome.completed)
        self.assertEqual(outcome.status, ExecutionAttemptStatus.FAILED)
        self.assertIn("worker failed", outcome.reason or "")

    def test_executor_return_type_is_structurally_checked(self) -> None:
        class BadExecutor:
            def execute(self, handoff: ExecutionHandoff):
                return {"unexpected": True}

        outcome = ExecutionAttemptService(BadExecutor()).attempt(self.handoff)

        self.assertFalse(outcome.completed)
        self.assertIn("invalid result type", outcome.reason or "")

    def test_executor_result_tool_identity_must_match_handoff(self) -> None:
        result = ToolResult(success=True, tool_name="other", invocation_id="inv-1")
        outcome = ExecutionAttemptService(StubExecutor(result=result)).attempt(self.handoff)

        self.assertFalse(outcome.completed)
        self.assertIn("tool identity", outcome.reason or "")

    def test_executor_result_invocation_identity_must_match_handoff(self) -> None:
        result = ToolResult(success=True, tool_name="echo", invocation_id="other")
        outcome = ExecutionAttemptService(StubExecutor(result=result)).attempt(self.handoff)

        self.assertFalse(outcome.completed)
        self.assertIn("invocation identity", outcome.reason or "")

    def test_attempt_requires_handoff(self) -> None:
        service = ExecutionAttemptService(
            StubExecutor(result=ToolResult(success=True, tool_name="echo", invocation_id="inv-1"))
        )
        with self.assertRaises(TypeError):
            service.attempt({"handoff_id": "handoff-1"})  # type: ignore[arg-type]

    def test_attempt_contract_requires_executor(self) -> None:
        with self.assertRaises(TypeError):
            ExecutionAttemptService(object())

    def test_attempt_result_is_immutable(self) -> None:
        tool_result = ToolResult(success=True, tool_name="echo", invocation_id="inv-1")
        outcome = ExecutionAttemptService(StubExecutor(result=tool_result)).attempt(self.handoff)

        with self.assertRaises(FrozenInstanceError):
            outcome.execution_id = "tampered"  # type: ignore[misc]

    def test_attempt_context_distinguishes_attempt_from_authority(self) -> None:
        tool_result = ToolResult(success=True, tool_name="echo", invocation_id="inv-1")
        context = ExecutionAttemptService(StubExecutor(result=tool_result)).attempt(
            self.handoff
        ).to_context()

        self.assertTrue(context["execution_attempted"])
        self.assertTrue(context["execution_completed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])

    def test_failed_attempt_requires_reason(self) -> None:
        with self.assertRaises(ExecutionAttemptError):
            ExecutionAttemptResult(
                execution_id="exec-1",
                handoff_id="handoff-1",
                tool_name="echo",
                invocation_id="inv-1",
                status=ExecutionAttemptStatus.FAILED,
            )


if __name__ == "__main__":
    unittest.main()
