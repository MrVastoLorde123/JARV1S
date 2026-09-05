from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_decision import (
    DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider,
    LearningWriteAdaptationEvaluationExecutionFeedbackAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecisionService,
)
from src.tools.learning_write_adaptation_evaluation_execution_result import (
    LearningWriteAdaptationEvaluationExecutionOutcome,
    LearningWriteAdaptationEvaluationExecutionOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-evaluation-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED,
            execution_result={"changed": True},
            result_fingerprint="fp-1",
        )
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(outcome)
        self.evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService().evaluate(feedback)
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackDecisionService()

    def test_success_evaluation_is_accepted(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(
                evaluation=self.evaluation
            )
        )
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT)
        self.assertEqual(decision.confidence, 0.5)

    def test_evaluation_decision_is_deterministic(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=self.evaluation)
        first = self.service.decide(context)
        second = self.service.decide(context)
        self.assertEqual(first.decision_id, second.decision_id)

    def test_full_lineage_is_preserved(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(
                evaluation=self.evaluation
            )
        )
        for field_name in (
            "evaluation_id", "feedback_id", "preparation_id", "admission_id", "proposal_id",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_id",
            "source_execution_id", "domain", "policy_id",
        ):
            with self.subTest(field_name=field_name):
                self.assertEqual(getattr(decision, field_name), getattr(self.evaluation, field_name))
        self.assertEqual(decision.decision_source_evaluation_id, self.evaluation.evaluation_id_from_feedback)

    def test_decision_is_immutable(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=self.evaluation)
        )
        with self.assertRaises(FrozenInstanceError):
            decision.action = LearningWriteAdaptationEvaluationExecutionFeedbackAction.REJECT  # type: ignore[misc]

    def test_metadata_is_immutable(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=self.evaluation)
        )
        with self.assertRaises(TypeError):
            decision.metadata["new"] = "blocked"  # type: ignore[index]

    def test_context_is_immutable_and_freezes_related_context(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(
            evaluation=self.evaluation,
            related_context={"nested": {"value": True}},
        )
        self.assertTrue(context.related_context["nested"]["value"])
        with self.assertRaises(TypeError):
            context.related_context["new"] = True  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            context.evaluation = self.evaluation  # type: ignore[misc]

    def test_decision_to_context_preserves_authority_wall(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=self.evaluation)
        )
        context = decision.to_context()
        self.assertEqual(context["adaptation_evaluation_execution_feedback_action"], "accept")
        self.assertFalse(context["execution_authorized"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])

    def test_invalid_evaluation_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation={"bad": True})  # type: ignore[arg-type]

    def test_invalid_action_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
                decision_source_evaluation_id="source-evaluation-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_id="execution-1", source_execution_id="source-execution-1",
                domain="semantic", policy_id="policy-1", action="bad", confidence=0.5,
                reason="test", metadata={},
            )  # type: ignore[arg-type]

    def test_confidence_must_be_bounded(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
                decision_source_evaluation_id="source-evaluation-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_id="execution-1", source_execution_id="source-execution-1",
                domain="semantic", policy_id="policy-1",
                action=LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT,
                confidence=1.1, reason="test", metadata={},
            )

    def test_decision_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                preparation_id="preparation-1", admission_id="admission-1", proposal_id="proposal-1",
                decision_source_evaluation_id="source-evaluation-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_id="execution-1", source_execution_id="source-execution-1",
                domain="semantic", policy_id="policy-1",
                action=LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT,
                confidence=0.5, reason="test", metadata={}, execution_authorized=True,
            )

    def test_service_rejects_provider_identity_mismatch(self) -> None:
        class _BadProvider(DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider):
            def decide(self, context):
                decision = super().decide(context)
                object.__setattr__(decision, "policy_id", "wrong-policy")
                return decision

        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionService(_BadProvider()).decide(
                LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=self.evaluation)
            )

    def test_failure_evaluation_defers(self) -> None:
        outcome = LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="execution-f",
            preparation_id="preparation-f",
            admission_id="admission-f",
            proposal_id="proposal-f",
            decision_id="decision-f",
            evaluation_id="evaluation-f",
            feedback_id="feedback-f",
            source_feedback_id="source-feedback-f",
            candidate_id="candidate-f",
            source_candidate_id="source-candidate-f",
            source_execution_id="source-execution-f",
            domain="procedural",
            policy_id="policy-f",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED,
            reason="applier unavailable",
        )
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(outcome)
        evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService().evaluate(feedback)
        decision = self.service.decide(LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext(evaluation=evaluation))
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationExecutionFeedbackAction.DEFER)


if __name__ == "__main__":
    unittest.main()
