from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackKind,
    LearningWriteAdaptationEvaluationExecutionFeedbackService,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError,
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService,
    LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind,
)
from src.tools.learning_write_adaptation_evaluation_execution_result import (
    LearningWriteAdaptationEvaluationExecutionOutcome,
    LearningWriteAdaptationEvaluationExecutionOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        success_outcome = LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="future-exec-1", preparation_id="prep-1", admission_id="admission-1",
            proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
            feedback_id="feedback-source-1", source_feedback_id="source-feedback-1",
            candidate_id="candidate-1", source_candidate_id="source-candidate-1",
            source_execution_id="source-execution-1", domain="semantic", policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED,
            execution_result={"changed": True}, result_fingerprint="fingerprint-1",
        )
        failure_outcome = LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="future-exec-2", preparation_id="prep-2", admission_id="admission-2",
            proposal_id="proposal-2", decision_id="decision-2", evaluation_id="evaluation-2",
            feedback_id="feedback-source-2", source_feedback_id="source-feedback-2",
            candidate_id="candidate-2", source_candidate_id="source-candidate-2",
            source_execution_id="source-execution-2", domain="procedural", policy_id="policy-2",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED,
            reason="applier unavailable",
        )
        feedback_service = LearningWriteAdaptationEvaluationExecutionFeedbackService()
        self.success_feedback = feedback_service.from_outcome(success_outcome)
        self.failure_feedback = feedback_service.from_outcome(failure_outcome)
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService()

    def test_success_feedback_becomes_success_signal(self) -> None:
        result = self.service.evaluate(self.success_feedback)
        self.assertEqual(result.signal, LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_SUCCESS_SIGNAL)
        self.assertEqual(result.confidence, 0.5)
        self.assertTrue(result.evidence["payload"]["execution_result"]["changed"])

    def test_failure_feedback_becomes_failure_signal(self) -> None:
        result = self.service.evaluate(self.failure_feedback)
        self.assertEqual(result.signal, LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_FAILURE_SIGNAL)
        self.assertEqual(result.evidence["payload"]["reason"], "applier unavailable")

    def test_exact_lineage_is_preserved(self) -> None:
        result = self.service.evaluate(self.success_feedback)
        for field in (
            "feedback_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_id",
            "source_execution_id", "domain", "policy_id",
        ):
            self.assertEqual(getattr(result, field), getattr(self.success_feedback, field))
        self.assertEqual(result.evaluation_id_from_feedback, self.success_feedback.evaluation_id)

    def test_evaluation_id_is_deterministic(self) -> None:
        self.assertEqual(self.service.evaluate(self.success_feedback).evaluation_id,
                         self.service.evaluate(self.success_feedback).evaluation_id)

    def test_evaluation_is_immutable(self) -> None:
        result = self.service.evaluate(self.success_feedback)
        with self.assertRaises(FrozenInstanceError):
            result.confidence = 0.9  # type: ignore[misc]

    def test_evidence_is_recursively_immutable(self) -> None:
        result = self.service.evaluate(self.success_feedback)
        with self.assertRaises(TypeError):
            result.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            result.evidence["payload"]["new"] = True  # type: ignore[index]

    def test_provenance_is_recursively_immutable(self) -> None:
        result = self.service.evaluate(self.success_feedback)
        with self.assertRaises(TypeError):
            result.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_preserves_authority_wall(self) -> None:
        context = self.service.evaluate(self.success_feedback).to_context()
        self.assertTrue(context["adaptation_evaluation"])
        for key in ("learning_written", "memory_mutated", "authority_granted", "authorization_granted",
                    "execution_requested", "retry_requested", "revocation_requested", "adaptation_truth_proven"):
            self.assertFalse(context[key])

    def test_invalid_feedback_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate({"bad": True})  # type: ignore[arg-type]

    def test_invalid_feedback_kind_is_rejected(self) -> None:
        invalid = object.__new__(self.success_feedback.__class__)
        for field in self.success_feedback.__dataclass_fields__:
            object.__setattr__(invalid, field, getattr(self.success_feedback, field))
        object.__setattr__(invalid, "kind", "bad")
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError):
            self.service.evaluate(invalid)

    def test_invalid_signal_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation(
                evaluation_id="eval", feedback_id="feedback", preparation_id="prep", admission_id="admission",
                proposal_id="proposal", decision_id="decision", evaluation_id_from_feedback="evaluation-source",
                source_feedback_id="source-feedback", candidate_id="candidate", source_candidate_id="source-candidate",
                execution_id="execution", source_execution_id="source-execution", domain="semantic", policy_id="policy",
                signal="bad", confidence=0.5, evidence={}, provenance={"source": "test"}, reason="test",
            )  # type: ignore[arg-type]

    def test_confidence_must_be_bounded(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError):
            LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation(
                evaluation_id="eval", feedback_id="feedback", preparation_id="prep", admission_id="admission",
                proposal_id="proposal", decision_id="decision", evaluation_id_from_feedback="evaluation-source",
                source_feedback_id="source-feedback", candidate_id="candidate", source_candidate_id="source-candidate",
                execution_id="execution", source_execution_id="source-execution", domain="semantic", policy_id="policy",
                signal=LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_SUCCESS_SIGNAL,
                confidence=1.1, evidence={}, provenance={"source": "test"}, reason="test",
            )


if __name__ == "__main__":
    unittest.main()
