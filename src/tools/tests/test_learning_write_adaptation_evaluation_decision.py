from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_feedback import (
    LearningWriteAdaptationFeedbackEvent,
    LearningWriteAdaptationFeedbackKind,
)
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationCandidate,
    LearningWriteAdaptationFeedbackEvaluationService,
    LearningWriteAdaptationFeedbackSignalKind,
)
from src.tools.learning_write_adaptation_evaluation_decision import (
    DeterministicLearningWriteAdaptationEvaluationDecisionProvider,
    LearningWriteAdaptationEvaluationAction,
    LearningWriteAdaptationEvaluationDecision,
    LearningWriteAdaptationEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationDecisionError,
    LearningWriteAdaptationEvaluationDecisionService,
)


class LearningWriteAdaptationEvaluationDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        feedback = LearningWriteAdaptationFeedbackEvent(
            feedback_id="adapt-feedback-1",
            execution_id="adapt-exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="adapt-candidate-1",
            source_feedback_id="learning-feedback-1",
            source_candidate_id="learning-candidate-1",
            domain="semantic",
            kind=LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS,
            payload={"changed": True},
            provenance={"source": "test"},
            reason="observed success",
        )
        self.evaluation = LearningWriteAdaptationFeedbackEvaluationService().evaluate(feedback)
        self.context = LearningWriteAdaptationEvaluationDecisionContext(
            evaluation=self.evaluation,
            related_context={"phase": "m22.30"},
        )
        self.service = LearningWriteAdaptationEvaluationDecisionService()

    def test_success_evaluation_is_accepted(self) -> None:
        decision = self.service.decide(self.context)
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationAction.ACCEPT)

    def test_low_confidence_evaluation_is_deferred(self) -> None:
        evaluation = LearningWriteAdaptationFeedbackEvaluationCandidate(
            evaluation_id=self.evaluation.evaluation_id,
            feedback_id=self.evaluation.feedback_id,
            source_feedback_id=self.evaluation.source_feedback_id,
            candidate_id=self.evaluation.candidate_id,
            execution_id=self.evaluation.execution_id,
            admission_id=self.evaluation.admission_id,
            proposal_id=self.evaluation.proposal_id,
            decision_id=self.evaluation.decision_id,
            source_candidate_id=self.evaluation.source_candidate_id,
            domain=self.evaluation.domain,
            signal=self.evaluation.signal,
            confidence=0.49,
            evidence=self.evaluation.evidence,
            provenance=self.evaluation.provenance,
            reason=self.evaluation.reason,
        )
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationDecisionContext(evaluation=evaluation)
        )
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationAction.DEFER)

    def test_failure_evaluation_is_deferred(self) -> None:
        evaluation = LearningWriteAdaptationFeedbackEvaluationCandidate(
            evaluation_id="eval-failure",
            feedback_id="adapt-feedback-failure",
            source_feedback_id="learning-feedback-1",
            candidate_id="adapt-candidate-failure",
            execution_id="adapt-exec-failure",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            source_candidate_id="learning-candidate-1",
            domain="semantic",
            signal=LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_FAILURE_SIGNAL,
            confidence=0.9,
            evidence={"failure": True},
            provenance={"source": "test"},
            reason="failed adaptation",
        )
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationDecisionContext(evaluation=evaluation)
        )
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationAction.DEFER)

    def test_exact_lineage_is_preserved(self) -> None:
        decision = self.service.decide(self.context)
        self.assertEqual(decision.evaluation_id, self.evaluation.evaluation_id)
        self.assertEqual(decision.feedback_id, self.evaluation.feedback_id)
        self.assertEqual(decision.source_feedback_id, self.evaluation.source_feedback_id)
        self.assertEqual(decision.candidate_id, self.evaluation.candidate_id)
        self.assertEqual(decision.execution_id, self.evaluation.execution_id)
        self.assertEqual(decision.admission_id, self.evaluation.admission_id)
        self.assertEqual(decision.proposal_id, self.evaluation.proposal_id)
        self.assertEqual(decision.source_candidate_id, self.evaluation.source_candidate_id)
        self.assertEqual(decision.domain, self.evaluation.domain)

    def test_decision_id_is_deterministic(self) -> None:
        first = self.service.decide(self.context)
        second = self.service.decide(self.context)
        self.assertEqual(first.decision_id, second.decision_id)

    def test_decision_is_immutable(self) -> None:
        decision = self.service.decide(self.context)
        with self.assertRaises(FrozenInstanceError):
            decision.action = LearningWriteAdaptationEvaluationAction.REJECT  # type: ignore[misc]

    def test_context_is_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.context.related_context = {}  # type: ignore[misc]

    def test_context_related_data_is_frozen(self) -> None:
        self.assertEqual(self.context.related_context["phase"], "m22.30")
        with self.assertRaises(TypeError):
            self.context.related_context["phase"] = "changed"  # type: ignore[index]

    def test_invalid_evaluation_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide({"bad": True})  # type: ignore[arg-type]

    def test_provider_output_identity_is_validated(self) -> None:
        class BadProvider:
            def decide(self, context: LearningWriteAdaptationEvaluationDecisionContext):
                evaluation = context.evaluation
                return LearningWriteAdaptationEvaluationDecision(
                    decision_id="bad-decision",
                    evaluation_id="wrong-evaluation",
                    feedback_id=evaluation.feedback_id,
                    source_feedback_id=evaluation.source_feedback_id,
                    candidate_id=evaluation.candidate_id,
                    execution_id=evaluation.execution_id,
                    admission_id=evaluation.admission_id,
                    proposal_id=evaluation.proposal_id,
                    source_candidate_id=evaluation.source_candidate_id,
                    domain=evaluation.domain,
                    action=LearningWriteAdaptationEvaluationAction.ACCEPT,
                    reason="bad provider",
                    confidence=0.5,
                )

        with self.assertRaises(LearningWriteAdaptationEvaluationDecisionError):
            LearningWriteAdaptationEvaluationDecisionService(BadProvider()).decide(self.context)

    def test_decision_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationDecisionError):
            LearningWriteAdaptationEvaluationDecision(
                decision_id="decision-2",
                evaluation_id=self.evaluation.evaluation_id,
                feedback_id=self.evaluation.feedback_id,
                source_feedback_id=self.evaluation.source_feedback_id,
                candidate_id=self.evaluation.candidate_id,
                execution_id=self.evaluation.execution_id,
                admission_id=self.evaluation.admission_id,
                proposal_id=self.evaluation.proposal_id,
                source_candidate_id=self.evaluation.source_candidate_id,
                domain=self.evaluation.domain,
                action=LearningWriteAdaptationEvaluationAction.ACCEPT,
                reason="must fail",
                confidence=0.5,
                adaptation_authorized=True,
            )

    def test_context_is_non_authorizing_and_non_writing(self) -> None:
        decision = self.service.decide(self.context)
        context = decision.to_context()
        self.assertFalse(context["adaptation_authorized"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])


if __name__ == "__main__":
    unittest.main()
