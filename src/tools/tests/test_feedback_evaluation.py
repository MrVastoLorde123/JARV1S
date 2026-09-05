from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.execution_feedback import ExecutionFeedbackService
from src.tools.execution_outcome import ExecutionOutcomeStatus
from src.tools.feedback_evaluation import (
    FeedbackEvaluationError,
    FeedbackEvaluationService,
    LearningCandidate,
    LearningSignalKind,
)


class FeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feedback_service = ExecutionFeedbackService()
        self.evaluation = FeedbackEvaluationService()

    def _feedback(self, status: ExecutionOutcomeStatus):
        from src.tools.execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
        from src.tools.execution_preparation import ExecutionHandoff
        from src.tools.models import ToolError, ToolResult
        from src.tools.execution_outcome import ExecutionOutcomeService

        handoff = ExecutionHandoff(
            handoff_id="handoff-1",
            authorization_id="auth-1",
            request_fingerprint="request-fp",
            decision_fingerprint="decision-fp",
            sandbox_profile_id="default",
            tool_name="echo",
            invocation_id="inv-1",
            arguments={"x": 1},
        )
        from src.tools.execution_attempt import ExecutionAttemptService

        if status is ExecutionOutcomeStatus.SUCCEEDED:
            result = ToolResult(success=True, tool_name="echo", content={"x": 1}, invocation_id="inv-1")
            attempt = ExecutionAttemptService(type("E", (), {"execute": lambda _, __: result})()).attempt(handoff)
        elif status is ExecutionOutcomeStatus.TOOL_FAILED:
            result = ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_failure", message="bad input"),
                invocation_id="inv-1",
            )
            attempt = ExecutionAttemptService(type("E", (), {"execute": lambda _, __: result})()).attempt(handoff)
        else:
            attempt = ExecutionAttemptResult(
                execution_id="exec-test",
                handoff_id=handoff.handoff_id,
                tool_name=handoff.tool_name,
                invocation_id=handoff.invocation_id,
                status=ExecutionAttemptStatus.FAILED,
                reason="worker unavailable",
            )
            # Use the deterministic execution id for the handoff.
            attempt = ExecutionAttemptResult(
                execution_id=ExecutionAttemptService(type("E", (), {"execute": lambda _, __: result})())._execution_id(handoff)
                if 'result' in locals() else ExecutionAttemptService(type("E", (), {"execute": lambda _, __: ToolResult(success=True, tool_name="echo")})())._execution_id(handoff),
                handoff_id=handoff.handoff_id,
                tool_name=handoff.tool_name,
                invocation_id=handoff.invocation_id,
                status=ExecutionAttemptStatus.FAILED,
                reason="worker unavailable",
            )
        outcome = ExecutionOutcomeService().interpret(attempt, handoff)
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
