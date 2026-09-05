from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
from src.tools.execution_feedback import (
    ExecutionFeedbackError,
    ExecutionFeedbackService,
    FeedbackKind,
)
from src.tools.execution_outcome import ExecutionOutcome, ExecutionOutcomeStatus
from src.tools.execution_preparation import ExecutionHandoff
from src.tools.models import ToolError, ToolResult


class ExecutionFeedbackTests(unittest.TestCase):
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
        self.execution_id = "exec-7d2a7d2f1f3e2d2f5b3e4e8c"

    def outcome_success(self) -> ExecutionOutcome:
        return ExecutionOutcome(
            execution_id=self.execution_id,
            handoff_id=self.handoff.handoff_id,
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionOutcomeStatus.SUCCEEDED,
            result=ToolResult(
                success=True,
                tool_name="echo",
                content={"value": 42},
                invocation_id="inv-1",
                metadata={"source": "stub"},
            ),
        )

    def outcome_tool_failure(self) -> ExecutionOutcome:
        return ExecutionOutcome(
            execution_id=self.execution_id,
            handoff_id=self.handoff.handoff_id,
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionOutcomeStatus.TOOL_FAILED,
            result=ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_error", message="bad input"),
                invocation_id="inv-1",
            ),
            reason="bad input",
        )

    def outcome_executor_failure(self) -> ExecutionOutcome:
        return ExecutionOutcome(
            execution_id=self.execution_id,
            handoff_id=self.handoff.handoff_id,
            tool_name="echo",
            invocation_id="inv-1",
            status=ExecutionOutcomeStatus.EXECUTOR_FAILED,
            reason="worker unavailable",
        )

    def test_success_outcome_becomes_success_feedback(self) -> None:
        event = ExecutionFeedbackService().from_outcome(self.outcome_success())

        self.assertEqual(event.kind, FeedbackKind.SUCCESS)
        self.assertEqual(event.payload["result"], {"value": 42})
        self.assertEqual(event.provenance["source"], "execution_outcome")
        self.assertEqual(event.provenance["execution_id"], self.execution_id)
        self.assertTrue(event.feedback_id.startswith("feedback-"))

    def test_tool_failure_is_preserved_as_tool_failure_feedback(self) -> None:
        event = ExecutionFeedbackService().from_outcome(self.outcome_tool_failure())

        self.assertEqual(event.kind, FeedbackKind.TOOL_FAILURE)
        self.assertEqual(event.reason, "bad input")
        self.assertEqual(event.payload["error"]["code"], "tool_error")

    def test_executor_failure_is_distinguished_from_tool_failure(self) -> None:
        event = ExecutionFeedbackService().from_outcome(self.outcome_executor_failure())

        self.assertEqual(event.kind, FeedbackKind.EXECUTOR_FAILURE)
        self.assertEqual(event.reason, "worker unavailable")
        self.assertIsNone(event.payload["result"])

    def test_feedback_identity_is_deterministic(self) -> None:
        service = ExecutionFeedbackService()
        first = service.from_outcome(self.outcome_success())
        second = service.from_outcome(self.outcome_success())

        self.assertEqual(first.feedback_id, second.feedback_id)
        self.assertEqual(first.provenance["payload_sha256"], second.provenance["payload_sha256"])

    def test_different_outcomes_get_different_feedback_identity(self) -> None:
        service = ExecutionFeedbackService()
        success = service.from_outcome(self.outcome_success())
        failure = service.from_outcome(self.outcome_tool_failure())

        self.assertNotEqual(success.feedback_id, failure.feedback_id)

    def test_feedback_event_is_immutable(self) -> None:
        event = ExecutionFeedbackService().from_outcome(self.outcome_success())

        with self.assertRaises(FrozenInstanceError):
            event.feedback_id = "tampered"  # type: ignore[misc]

    def test_feedback_context_is_non_authorizing_and_non_learning(self) -> None:
        context = ExecutionFeedbackService().from_outcome(self.outcome_success()).to_context()

        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["learning_written"])

    def test_feedback_requires_execution_outcome(self) -> None:
        with self.assertRaises(TypeError):
            ExecutionFeedbackService().from_outcome({"execution_id": self.execution_id})  # type: ignore[arg-type]

    def test_feedback_rejects_success_reason(self) -> None:
        with self.assertRaises(ExecutionFeedbackError):
            from src.tools.execution_feedback import ExecutionFeedbackEvent

            ExecutionFeedbackEvent(
                feedback_id="feedback-1",
                execution_id=self.execution_id,
                handoff_id="handoff-1",
                tool_name="echo",
                invocation_id="inv-1",
                kind=FeedbackKind.SUCCESS,
                payload={},
                provenance={"source": "execution_outcome"},
                reason="should not exist",
            )

    def test_feedback_rejects_failed_kind_without_reason(self) -> None:
        with self.assertRaises(ExecutionFeedbackError):
            from src.tools.execution_feedback import ExecutionFeedbackEvent

            ExecutionFeedbackEvent(
                feedback_id="feedback-1",
                execution_id=self.execution_id,
                handoff_id="handoff-1",
                tool_name="echo",
                invocation_id="inv-1",
                kind=FeedbackKind.TOOL_FAILURE,
                payload={},
                provenance={"source": "execution_outcome"},
            )


if __name__ == "__main__":
    unittest.main()
