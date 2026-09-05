from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision import (
    DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService,
)


class M22_46_Tests(unittest.TestCase):
    def setUp(self) -> None:
        common = {
            "feedback_id": "feedback-1",
            "outcome_id": "outcome-1",
            "execution_id": "execution-1",
            "preparation_id": "preparation-1",
            "admission_id": "admission-1",
            "proposal_id": "proposal-1",
            "decision_id": "decision-1",
            "evaluation_id_from_feedback": "evaluation-from-feedback-1",
            "decision_source_evaluation_id": "decision-source-evaluation-1",
            "source_feedback_id": "source-feedback-1",
            "candidate_id": "candidate-1",
            "source_candidate_id": "source-candidate-1",
            "execution_source_id": "execution-source-1",
            "source_execution_id": "source-execution-1",
            "source_admission_id": "source-admission-1",
            "proposal_source_id": "proposal-source-1",
            "domain": "semantic",
            "source_policy_id": "source-policy-1",
            "policy_id": "policy-1",
        }
        self.evaluation = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-1",
            **common,
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
            confidence=0.5,
            evidence={"payload": {"observed": True}},
            provenance={"source": "test"},
            reason="observed integrity success",
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService()

    def test_success_evaluation_is_accepted(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        self.assertEqual(
            decision.action,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.ACCEPT,
        )
        self.assertEqual(decision.confidence, 0.5)

    def test_failure_evaluation_defers(self) -> None:
        failure = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-failure",
            feedback_id="feedback-failure",
            outcome_id="outcome-failure",
            execution_id="execution-failure",
            preparation_id="preparation-failure",
            admission_id="admission-failure",
            proposal_id="proposal-failure",
            decision_id="decision-failure",
            evaluation_id_from_feedback="evaluation-from-feedback-failure",
            decision_source_evaluation_id="decision-source-evaluation-failure",
            source_feedback_id="source-feedback-failure",
            candidate_id="candidate-failure",
            source_candidate_id="source-candidate-failure",
            execution_source_id="execution-source-failure",
            source_execution_id="source-execution-failure",
            source_admission_id="source-admission-failure",
            proposal_source_id="proposal-source-failure",
            domain="procedural",
            source_policy_id="source-policy-failure",
            policy_id="policy-failure",
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL,
            confidence=0.9,
            evidence={"payload": {"observed": False}},
            provenance={"source": "test"},
            reason="observed integrity failure",
        )
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=failure
            )
        )
        self.assertEqual(
            decision.action,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.DEFER,
        )

    def test_low_confidence_defers(self) -> None:
        low = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id="evaluation-low",
            feedback_id="feedback-low",
            outcome_id="outcome-low",
            execution_id="execution-low",
            preparation_id="preparation-low",
            admission_id="admission-low",
            proposal_id="proposal-low",
            decision_id="decision-low",
            evaluation_id_from_feedback="evaluation-from-feedback-low",
            decision_source_evaluation_id="decision-source-evaluation-low",
            source_feedback_id="source-feedback-low",
            candidate_id="candidate-low",
            source_candidate_id="source-candidate-low",
            execution_source_id="execution-source-low",
            source_execution_id="source-execution-low",
            source_admission_id="source-admission-low",
            proposal_source_id="proposal-source-low",
            domain="semantic",
            source_policy_id="source-policy-low",
            policy_id="policy-low",
            signal=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL,
            confidence=0.49,
            evidence={"payload": {}},
            provenance={"source": "test"},
            reason="low confidence",
        )
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=low
            )
        )
        self.assertEqual(
            decision.action,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.DEFER,
        )

    def test_decision_id_is_deterministic(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
            evaluation=self.evaluation
        )
        first = self.service.decide(context)
        second = self.service.decide(context)
        self.assertEqual(first.decision_id, second.decision_id)

    def test_decision_id_is_distinct_from_evaluation_and_feedback(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        self.assertNotEqual(decision.decision_id, decision.evaluation_id)
        self.assertNotEqual(decision.decision_id, decision.feedback_id)
        self.assertNotEqual(decision.decision_id, decision.execution_id)

    def test_full_lineage_is_preserved(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        for field_name in (
            "evaluation_id", "feedback_id", "outcome_id", "execution_id", "preparation_id",
            "admission_id", "proposal_id", "decision_id", "evaluation_id_from_feedback",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id",
            "source_execution_id", "source_admission_id", "proposal_source_id", "domain",
            "source_policy_id", "policy_id",
        ):
            with self.subTest(field_name=field_name):
                self.assertEqual(getattr(decision, field_name), getattr(self.evaluation, field_name))
        self.assertEqual(decision.decision_source_evaluation_id, self.evaluation.evaluation_id)

    def test_decision_is_immutable(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        with self.assertRaises(FrozenInstanceError):
            decision.action = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.REJECT  # type: ignore[misc]

    def test_metadata_is_immutable(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        with self.assertRaises(TypeError):
            decision.metadata["new"] = "blocked"  # type: ignore[index]

    def test_context_freezes_related_context(self) -> None:
        context = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
            evaluation=self.evaluation,
            related_context={"nested": {"value": True}},
        )
        self.assertTrue(context.related_context["nested"]["value"])
        with self.assertRaises(TypeError):
            context.related_context["new"] = True  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            context.evaluation = self.evaluation  # type: ignore[misc]

    def test_context_preserves_authority_wall(self) -> None:
        decision = self.service.decide(
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                evaluation=self.evaluation
            )
        )
        context = decision.to_context()
        self.assertFalse(context["execution_authorized"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])

    def test_invalid_evaluation_type_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(evaluation={"bad": True})  # type: ignore[arg-type]

    def test_invalid_action_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                outcome_id="outcome-1", execution_id="execution-1", preparation_id="preparation-1",
                admission_id="admission-1", proposal_id="proposal-1", decision_source_evaluation_id="evaluation-1",
                evaluation_id_from_feedback="evaluation-from-feedback-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="execution-source-1", source_execution_id="source-execution-1",
                source_admission_id="source-admission-1", proposal_source_id="proposal-source-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                action="bad", confidence=0.5, reason="test", metadata={},  # type: ignore[arg-type]
            )

    def test_confidence_must_be_bounded(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                outcome_id="outcome-1", execution_id="execution-1", preparation_id="preparation-1",
                admission_id="admission-1", proposal_id="proposal-1", decision_source_evaluation_id="evaluation-1",
                evaluation_id_from_feedback="evaluation-from-feedback-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="execution-source-1", source_execution_id="source-execution-1",
                source_admission_id="source-admission-1", proposal_source_id="proposal-source-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.ACCEPT,
                confidence=1.1, reason="test", metadata={},
            )

    def test_decision_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
                decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
                outcome_id="outcome-1", execution_id="execution-1", preparation_id="preparation-1",
                admission_id="admission-1", proposal_id="proposal-1", decision_source_evaluation_id="evaluation-1",
                evaluation_id_from_feedback="evaluation-from-feedback-1", source_feedback_id="source-feedback-1",
                candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="execution-source-1", source_execution_id="source-execution-1",
                source_admission_id="source-admission-1", proposal_source_id="proposal-source-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                action=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationAction.ACCEPT,
                confidence=0.5, reason="test", metadata={}, execution_authorized=True,
            )

    def test_service_rejects_provider_identity_mismatch(self) -> None:
        class _BadProvider(DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider):
            def decide(self, context):
                decision = super().decide(context)
                object.__setattr__(decision, "policy_id", "wrong-policy")
                return decision

        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService(
                _BadProvider()
            ).decide(
                LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext(
                    evaluation=self.evaluation
                )
            )


if __name__ == "__main__":
    unittest.main()
