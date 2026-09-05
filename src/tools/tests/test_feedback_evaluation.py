from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptService, ExecutionAttemptStatus
from src.tools.execution_feedback import ExecutionFeedbackService
from src.tools.execution_outcome import ExecutionOutcomeService, ExecutionOutcomeStatus
from src.tools.execution_preparation import ExecutionHandoff
from src.tools.feedback_evaluation import (
    FeedbackEvaluationError,
    FeedbackEvaluationService,
    LearningCandidate,
    LearningSignalKind,
)
from src.tools.models import ToolError, ToolResult


class StubExecutor:
    def __init__(self, result: ToolResult | None = None) -> None:
        self.result = result

    def execute(self, handoff: ExecutionHandoff) -> ToolResult:
        assert self.result is not None
        return self.result


class FeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feedback_service = ExecutionFeedbackService()
        self.evaluation = FeedbackEvaluationService()
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

    def _feedback(self, status: ExecutionOutcomeStatus):
        if status is ExecutionOutcomeStatus.SUCCEEDED:
            tool_result = ToolResult(
                success=True,
                tool_name="echo",
                content={"x": 1, "nested": {"value": 2}},
                invocation_id="inv-1",
            )
            attempt = ExecutionAttemptService(StubExecutor(tool_result)).attempt(self.handoff)
        elif status is ExecutionOutcomeStatus.TOOL_FAILED:
            tool_result = ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_failure", message="bad input"),
                invocation_id="inv-1",
            )
            attempt = ExecutionAttemptService(StubExecutor(tool_result)).attempt(self.handoff)
        else:
            execution_id = ExecutionAttemptService(
                StubExecutor(ToolResult(success=True, tool_name="echo"))
            )._execution_id(self.handoff)
            attempt = ExecutionAttemptResult(
                execution_id=execution_id,
                handoff_id=self.handoff.handoff_id,
                tool_name=self.handoff.tool_name,
                invocation_id=self.handoff.invocation_id,
                status=ExecutionAttemptStatus.FAILED,
                reason="worker unavailable",
            )

        outcome = ExecutionOutcomeService().interpret(attempt, self.handoff)
        return self.feedback_service.from_outcome(outcome)

    def test_success_feedback_becomes_positive_learning_signal(self) -> None:
        candidate = self.evaluation.evaluate(self._feedback(ExecutionOutcomeStatus.SUCCEEDED))

        self.assertEqual(candidate.signal, LearningSignalKind.SUCCESS_SIGNAL)
        self.assertEqual(candidate.confidence, 0.5)
        self.assertIn("successful execution", candidate.reason)

    def test_tool_failure_feedback_becomes_negative_learning_signal(self) -> None:
        candidate = self.evaluation.evaluate(self._feedback(ExecutionOutcomeStatus.TOOL_FAILED))

        self.assertEqual(candidate.signal, LearningSignalKind.TOOL_FAILURE_SIGNAL)
        self.assertIn("requiring evaluation", candidate.reason)

    def test_executor_failure_remains_operational_signal(self) -> None:
        candidate = self.evaluation.evaluate(self._feedback(ExecutionOutcomeStatus.EXECUTOR_FAILED))

        self.assertEqual(candidate.signal, LearningSignalKind.EXECUTOR_FAILURE_SIGNAL)

    def test_candidate_identity_is_deterministic(self) -> None:
        feedback = self._feedback(ExecutionOutcomeStatus.SUCCEEDED)
        first = self.evaluation.evaluate(feedback)
        second = self.evaluation.evaluate(feedback)

        self.assertEqual(first.candidate_id, second.candidate_id)

    def test_candidate_preserves_feedback_provenance(self) -> None:
        feedback = self._feedback(ExecutionOutcomeStatus.SUCCEEDED)
        candidate = self.evaluation.evaluate(feedback)

        self.assertEqual(candidate.feedback_id, feedback.feedback_id)
        self.assertEqual(candidate.execution_id, feedback.execution_id)
        self.assertEqual(candidate.handoff_id, feedback.handoff_id)
        self.assertEqual(candidate.provenance["feedback_id"], feedback.feedback_id)

    def test_candidate_context_requires_later_learning_decision(self) -> None:
        context = self.evaluation.evaluate(
            self._feedback(ExecutionOutcomeStatus.SUCCEEDED)
        ).to_context()

        self.assertTrue(context["learning_candidate"])
        self.assertTrue(context["learning_decision_required"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_candidate_is_immutable(self) -> None:
        candidate = self.evaluation.evaluate(self._feedback(ExecutionOutcomeStatus.SUCCEEDED))

        with self.assertRaises(FrozenInstanceError):
            candidate.confidence = 1.0  # type: ignore[misc]
        with self.assertRaises(TypeError):
            candidate.evidence["new"] = "value"  # type: ignore[index]
        with self.assertRaises(TypeError):
            candidate.evidence["payload"]["new"] = "value"  # type: ignore[index]
        with self.assertRaises(TypeError):
            candidate.provenance["new"] = "value"  # type: ignore[index]

    def test_invalid_feedback_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.evaluation.evaluate({"feedback_id": "bad"})  # type: ignore[arg-type]

    def test_invalid_candidate_invariants_are_rejected(self) -> None:
        with self.assertRaises(FeedbackEvaluationError):
            LearningCandidate(
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                execution_id="exec-1",
                handoff_id="handoff-1",
                tool_name="echo",
                signal=LearningSignalKind.SUCCESS_SIGNAL,
                confidence=2.0,
                evidence={},
                provenance={"source": "test"},
                reason="invalid confidence",
            )


if __name__ == "__main__":
    unittest.main()
