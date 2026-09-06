"""Focused tests for M23.89 application outcome feedback evaluation v3."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status as OutcomeStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3 as Feedback,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status as FeedbackStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3 as Evaluation,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Service as EvaluationService,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status as EvaluationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status as ApplicationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status as IntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status as DecisionStatus,
)


class M23_89OutcomeFeedbackEvaluationV3Tests(unittest.TestCase):
    def _feedback(self, outcome: str = "success") -> Feedback:
        states = {
            "success": (OutcomeStatus.SUCCESS, ApplicationStatus.APPLIED, DecisionStatus.ACCEPTED, "executor-1", None, FeedbackStatus.SUCCESS_FEEDBACK),
            "failure": (OutcomeStatus.FAILURE, ApplicationStatus.NOT_APPLIED, DecisionStatus.ACCEPTED, None, "learning applier failed", FeedbackStatus.FAILURE_FEEDBACK),
            "rejected": (OutcomeStatus.REJECTED, ApplicationStatus.NOT_APPLIED, DecisionStatus.REJECTED, None, None, FeedbackStatus.REJECTION_FEEDBACK),
        }
        outcome_status, application_status, decision_status, executor_id, failure_reason, feedback_status = states[outcome]
        return Feedback(
            feedback_id="feedback-1", classification_id="classification-1", integrity_id="integrity-1", application_id="application-1",
            decision_id="decision-1", proposal_id="proposal-1", source_proposal_id="proposal-source-1", eligibility_id="eligibility-1",
            eligibility_source_id="eligibility-source-1", integrity_source_id="integrity-source-1", signal_id="signal-1", evaluation_id="evaluation-upstream-1",
            classification_source_id="integrity-1", application_source_id="application-source-1", source_integrity_id="source-integrity-1",
            feedback_signal_id="feedback-signal-1", feedback_source_id="classification-1", source_evaluation_id="source-evaluation-1",
            execution_id="execution-1", handoff_id="handoff-1", authorization_id="authorization-1", validation_id="validation-1",
            source_signal_id="source-signal-1", outcome_id="outcome-1", preparation_id="preparation-1", assessment_id=None,
            environment_id="environment-1", expected_model_id="expected-model-1", observed_model_id="observed-model-1", confidence=0.9,
            signal_fingerprint="a" * 64, upstream_proposal_fingerprint="b" * 64, handoff_fingerprint="c" * 64, result_fingerprint="d" * 64,
            source_application_fingerprint="e" * 64, application_fingerprint="f" * 64, authority_principal_id=None, executor_id=executor_id,
            proposal_kind="bounded-learning-adaptation", proposal_status="PROPOSED", decision_status=decision_status, application_status=application_status,
            integrity_status=IntegrityStatus.VALID, outcome_status=outcome_status, feedback_status=feedback_status,
            failure_reason=failure_reason, reasons={"feedback": feedback_status.value}, lineage={"feedback_id": "feedback-1"},
        )

    def _evaluation_kwargs(self, source: Feedback, **overrides):
        values = {
            "evaluation_id": "evaluation-x",
            "feedback_id": source.feedback_id,
            "feedback_source_id": source.feedback_source_id,
            "classification_id": source.classification_id,
            "integrity_id": source.integrity_id,
            "application_id": source.application_id,
            "decision_id": source.decision_id,
            "proposal_id": source.proposal_id,
            "outcome_id": source.outcome_id,
            "outcome_status": source.outcome_status,
            "feedback_status": source.feedback_status,
            "confidence": source.confidence,
            "signal_fingerprint": source.signal_fingerprint,
            "result_fingerprint": source.result_fingerprint,
            "application_fingerprint": source.application_fingerprint,
            "failure_reason": source.failure_reason,
            "evaluation_status": EvaluationStatus.INFORMATIVE,
            "reasons": source.reasons,
            "lineage": source.lineage,
        }
        values.update(overrides)
        return values

    def _evaluate(self, outcome: str = "success", status: EvaluationStatus = EvaluationStatus.INFORMATIVE) -> Evaluation:
        return EvaluationService().evaluate(self._feedback(outcome), evaluation_id="evaluation-1", evaluation_status=status)

    def test_success_feedback_can_be_evaluated(self):
        result = self._evaluate("success")
        self.assertEqual(result.evaluation_status, EvaluationStatus.INFORMATIVE)
        self.assertEqual(result.outcome_status, OutcomeStatus.SUCCESS)

    def test_failure_feedback_can_be_evaluated_and_preserves_reason(self):
        result = self._evaluate("failure", EvaluationStatus.AMBIGUOUS)
        self.assertEqual(result.evaluation_status, EvaluationStatus.AMBIGUOUS)
        self.assertEqual(result.failure_reason, "learning applier failed")

    def test_rejection_feedback_can_be_evaluated(self):
        result = self._evaluate("rejected", EvaluationStatus.NON_INFORMATIVE)
        self.assertEqual(result.evaluation_status, EvaluationStatus.NON_INFORMATIVE)
        self.assertEqual(result.feedback_status, FeedbackStatus.REJECTION_FEEDBACK)
        self.assertIsNone(result.failure_reason)

    def test_new_evaluation_identity_is_distinct_and_feedback_provenance_is_preserved(self):
        source = self._feedback()
        result = EvaluationService().evaluate(source, evaluation_id="evaluation-new", evaluation_status=EvaluationStatus.INFORMATIVE)
        self.assertNotEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.feedback_id, source.feedback_id)
        self.assertEqual(result.feedback_source_id, source.feedback_source_id)
        self.assertEqual(result.classification_id, source.classification_id)
        self.assertEqual(result.integrity_id, source.integrity_id)

    def test_fingerprints_and_confidence_are_preserved(self):
        source = self._feedback()
        result = EvaluationService().evaluate(source, evaluation_id="evaluation-2", evaluation_status=EvaluationStatus.INFORMATIVE)
        for name in ("signal_fingerprint", "result_fingerprint", "application_fingerprint", "confidence"):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_wrong_feedback_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EvaluationService().evaluate(object(), evaluation_id="evaluation-3", evaluation_status=EvaluationStatus.INFORMATIVE)

    def test_blank_evaluation_id_fails_closed(self):
        with self.assertRaises(ValueError):
            EvaluationService().evaluate(self._feedback(), evaluation_id=" ", evaluation_status=EvaluationStatus.INFORMATIVE)

    def test_wrong_evaluation_status_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EvaluationService().evaluate(self._feedback(), evaluation_id="evaluation-4", evaluation_status="INFORMATIVE")

    def test_feedback_and_outcome_status_mismatch_is_rejected(self):
        source = self._feedback()
        with self.assertRaises(ValueError):
            Evaluation(**self._evaluation_kwargs(source, evaluation_id="evaluation-5", outcome_status=OutcomeStatus.FAILURE, evaluation_status=EvaluationStatus.AMBIGUOUS))

    def test_failure_evaluation_requires_failure_evidence(self):
        source = self._feedback("failure")
        with self.assertRaises(ValueError):
            Evaluation(**self._evaluation_kwargs(source, evaluation_id="evaluation-6", failure_reason=None, outcome_status=OutcomeStatus.FAILURE, evaluation_status=EvaluationStatus.AMBIGUOUS))

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = EvaluationService().evaluate(
            self._feedback(), evaluation_id="evaluation-7", evaluation_status=EvaluationStatus.INFORMATIVE,
            reasons={"nested": {"items": ["x"]}}, lineage={"nested": {"items": ["y"]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        self.assertIsInstance(result.reasons["nested"]["items"], tuple)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["new"] = "value"
        self.assertIsInstance(result.lineage["nested"], MappingProxyType)

    def test_source_is_not_mutated(self):
        source = self._feedback("failure")
        before = source.__dict__.copy()
        EvaluationService().evaluate(source, evaluation_id="evaluation-8", evaluation_status=EvaluationStatus.AMBIGUOUS)
        self.assertEqual(source.__dict__, before)

    def test_evaluation_is_advisory_only(self):
        result = self._evaluate("success")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_evaluation_is_frozen(self):
        result = self._evaluate("success")
        with self.assertRaises(Exception):
            result.evaluation_status = EvaluationStatus.AMBIGUOUS


if __name__ == "__main__":
    unittest.main()
