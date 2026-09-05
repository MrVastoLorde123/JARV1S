from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.execution_attempt import ExecutionAttemptService, ExecutionAttemptResult, ExecutionAttemptStatus
from src.tools.execution_feedback import ExecutionFeedbackService
from src.tools.execution_outcome import ExecutionOutcomeService, ExecutionOutcomeStatus
from src.tools.execution_preparation import ExecutionHandoff
from src.tools.feedback_evaluation import FeedbackEvaluationService
from src.tools.learning_decision import (
    DeterministicLearningDecisionProvider,
    LearningAction,
    LearningDecision,
    LearningDecisionContext,
    LearningDecisionError,
    LearningDecisionService,
)
from src.tools.models import ToolError, ToolResult


class LearningDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feedback = ExecutionFeedbackService()
        self.evaluation = FeedbackEvaluationService()
        self.service = LearningDecisionService()

    def _candidate(self, status: ExecutionOutcomeStatus):
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

        if status is ExecutionOutcomeStatus.SUCCEEDED:
            result = ToolResult(success=True, tool_name="echo", content={"x": 1}, invocation_id="inv-1")

            class Executor:
                def execute(self, prepared_handoff):
                    return result

            attempt = ExecutionAttemptService(Executor()).attempt(handoff)
        elif status is ExecutionOutcomeStatus.TOOL_FAILED:
            result = ToolResult(
                success=False,
                tool_name="echo",
                error=ToolError(code="tool_failure", message="bad input"),
                invocation_id="inv-1",
            )

            class Executor:
                def execute(self, prepared_handoff):
                    return result

            attempt = ExecutionAttemptService(Executor()).attempt(handoff)
        else:
            class Executor:
                def execute(self, prepared_handoff):
                    raise RuntimeError("worker unavailable")

            attempt = ExecutionAttemptService(Executor()).attempt(handoff)

        outcome = ExecutionOutcomeService().interpret(attempt, handoff)
        return self.evaluation.evaluate(self.feedback.from_outcome(outcome))

    def test_success_candidate_is_accepted(self) -> None:
        decision = self.service.decide(LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.SUCCEEDED)))
        self.assertEqual(decision.action, LearningAction.ACCEPT)

    def test_tool_failure_candidate_is_accepted(self) -> None:
        decision = self.service.decide(LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.TOOL_FAILED)))
        self.assertEqual(decision.action, LearningAction.ACCEPT)

    def test_executor_failure_candidate_is_deferred(self) -> None:
        decision = self.service.decide(LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.EXECUTOR_FAILED)))
        self.assertEqual(decision.action, LearningAction.DEFER)

    def test_decision_is_deterministic(self) -> None:
        context = LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.SUCCEEDED))
        first = self.service.decide(context)
        second = self.service.decide(context)
        self.assertEqual(first.decision_id, second.decision_id)

    def test_candidate_identity_is_preserved(self) -> None:
        candidate = self._candidate(ExecutionOutcomeStatus.SUCCEEDED)
        decision = self.service.decide(LearningDecisionContext(candidate))
        self.assertEqual(decision.candidate_id, candidate.candidate_id)

    def test_decision_is_non_authorizing_and_non_writing(self) -> None:
        decision = self.service.decide(LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.SUCCEEDED)))
        context = decision.to_context()
        self.assertFalse(context["learning_write_allowed"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_decision_is_immutable(self) -> None:
        decision = self.service.decide(LearningDecisionContext(self._candidate(ExecutionOutcomeStatus.SUCCEEDED)))
        with self.assertRaises(FrozenInstanceError):
            decision.action = LearningAction.REJECT  # type: ignore[misc]

    def test_identity_mismatch_is_rejected(self) -> None:
        candidate = self._candidate(ExecutionOutcomeStatus.SUCCEEDED)
        bad = LearningDecision(
            decision_id="decision-1",
            candidate_id="other-candidate",
            action=LearningAction.ACCEPT,
            reason="bad",
            confidence=0.5,
        )

        class Provider(DeterministicLearningDecisionProvider):
            def decide(self, context):
                return bad

        with self.assertRaises(LearningDecisionError):
            LearningDecisionService(Provider()).decide(LearningDecisionContext(candidate))

    def test_learning_decision_cannot_grant_write_authority(self) -> None:
        candidate = self._candidate(ExecutionOutcomeStatus.SUCCEEDED)
        with self.assertRaises(LearningDecisionError):
            LearningDecision(
                decision_id="decision-1",
                candidate_id=candidate.candidate_id,
                action=LearningAction.ACCEPT,
                reason="bad authority",
                confidence=0.5,
                learning_write_allowed=True,
            )

    def test_invalid_context_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide({"candidate": "bad"})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
