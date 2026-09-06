"""Focused tests for M23.90 application learning adaptation learning signal v4."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3 as Evaluation,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status as EvaluationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status as OutcomeStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status as FeedbackStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4 as Signal,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Service as SignalService,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Status as SignalStatus,
)


def evaluation(status: EvaluationStatus, outcome: OutcomeStatus = OutcomeStatus.SUCCESS) -> Evaluation:
    feedback_status = {
        OutcomeStatus.SUCCESS: FeedbackStatus.SUCCESS_FEEDBACK,
        OutcomeStatus.FAILURE: FeedbackStatus.FAILURE_FEEDBACK,
        OutcomeStatus.REJECTED: FeedbackStatus.REJECTION_FEEDBACK,
    }[outcome]
    failure_reason = "applier failed" if outcome is OutcomeStatus.FAILURE else None
    return Evaluation(
        evaluation_id="evaluation-90",
        feedback_id="feedback-90",
        feedback_source_id="feedback-source-90",
        classification_id="classification-90",
        integrity_id="integrity-90",
        application_id="application-90",
        decision_id="decision-90",
        proposal_id="proposal-90",
        outcome_id="outcome-90",
        outcome_status=outcome,
        feedback_status=feedback_status,
        confidence=0.91,
        signal_fingerprint="a" * 64,
        result_fingerprint="b" * 64,
        application_fingerprint="c" * 64,
        failure_reason=failure_reason,
        evaluation_status=status,
        reasons={"evaluation": status.value},
        lineage={"evaluation_id": "evaluation-90"},
    )


class M23_90ApplicationLearningSignalV4Tests(unittest.TestCase):
    def test_success_informative_maps_to_positive_signal(self):
        result = SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE), signal_id="signal-new")
        self.assertEqual(result.signal_status, SignalStatus.POSITIVE_SIGNAL)
        self.assertTrue(result.is_learning_signal)

    def test_failure_informative_maps_to_negative_signal_and_preserves_reason(self):
        result = SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE, OutcomeStatus.FAILURE), signal_id="signal-new")
        self.assertEqual(result.signal_status, SignalStatus.NEGATIVE_SIGNAL)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_rejection_informative_maps_to_rejection_signal(self):
        result = SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE, OutcomeStatus.REJECTED), signal_id="signal-new")
        self.assertEqual(result.signal_status, SignalStatus.REJECTION_SIGNAL)

    def test_ambiguous_evaluation_maps_to_ambiguous_signal(self):
        result = SignalService().emit(evaluation(EvaluationStatus.AMBIGUOUS), signal_id="signal-new")
        self.assertEqual(result.signal_status, SignalStatus.AMBIGUOUS_SIGNAL)

    def test_non_informative_evaluation_maps_to_non_informative_signal(self):
        result = SignalService().emit(evaluation(EvaluationStatus.NON_INFORMATIVE), signal_id="signal-new")
        self.assertEqual(result.signal_status, SignalStatus.NON_INFORMATIVE_SIGNAL)

    def test_new_signal_identity_and_evaluation_provenance_are_preserved(self):
        source = evaluation(EvaluationStatus.INFORMATIVE)
        result = SignalService().emit(source, signal_id="signal-new")
        self.assertNotEqual(result.signal_id, source.evaluation_id)
        self.assertEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.feedback_id, source.feedback_id)
        self.assertEqual(result.feedback_source_id, source.feedback_source_id)
        self.assertEqual(result.classification_id, source.classification_id)
        self.assertEqual(result.integrity_id, source.integrity_id)

    def test_fingerprints_and_confidence_are_preserved(self):
        source = evaluation(EvaluationStatus.INFORMATIVE)
        result = SignalService().emit(source, signal_id="signal-new")
        for name in ("signal_fingerprint", "result_fingerprint", "application_fingerprint", "confidence"):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            SignalService().emit(object(), signal_id="signal-new")

    def test_blank_signal_id_fails_closed(self):
        with self.assertRaises(ValueError):
            SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE), signal_id=" ")

    def test_signal_status_mismatch_is_rejected(self):
        source = evaluation(EvaluationStatus.INFORMATIVE)
        with self.assertRaises(ValueError):
            Signal(
                signal_id="signal-new",
                evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id,
                feedback_source_id=source.feedback_source_id,
                classification_id=source.classification_id,
                integrity_id=source.integrity_id,
                application_id=source.application_id,
                decision_id=source.decision_id,
                proposal_id=source.proposal_id,
                outcome_id=source.outcome_id,
                outcome_status=source.outcome_status,
                feedback_status=source.feedback_status,
                confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint,
                result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint,
                failure_reason=source.failure_reason,
                evaluation_status=source.evaluation_status,
                signal_status=SignalStatus.NEGATIVE_SIGNAL,
            )

    def test_failure_signal_requires_failure_evidence(self):
        source = evaluation(EvaluationStatus.INFORMATIVE, OutcomeStatus.FAILURE)
        with self.assertRaises(ValueError):
            Signal(
                signal_id="signal-new",
                evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id,
                feedback_source_id=source.feedback_source_id,
                classification_id=source.classification_id,
                integrity_id=source.integrity_id,
                application_id=source.application_id,
                decision_id=source.decision_id,
                proposal_id=source.proposal_id,
                outcome_id=source.outcome_id,
                outcome_status=source.outcome_status,
                feedback_status=source.feedback_status,
                confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint,
                result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint,
                failure_reason=None,
                evaluation_status=source.evaluation_status,
                signal_status=SignalStatus.NEGATIVE_SIGNAL,
            )

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = SignalService().emit(
            evaluation(EvaluationStatus.INFORMATIVE),
            signal_id="signal-new",
            reasons={"nested": {"items": ["x"]}},
            lineage={"nested": {"items": ["y"]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        self.assertIsInstance(result.reasons["nested"]["items"], tuple)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["x"] = "blocked"
        self.assertIsInstance(result.lineage["nested"], MappingProxyType)

    def test_source_is_not_mutated(self):
        source = evaluation(EvaluationStatus.AMBIGUOUS)
        before = source.__dict__.copy()
        SignalService().emit(source, signal_id="signal-new")
        self.assertEqual(source.__dict__, before)

    def test_signal_is_advisory_only(self):
        result = SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE), signal_id="signal-new")
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.is_observational)
        for property_name in (
            "grants_authority", "authorizes_retry", "requests_retry", "updates_model", "mutates_memory",
            "mutates_policy", "mutates_persistence", "schedules_work", "executes",
        ):
            self.assertFalse(getattr(result, property_name))

    def test_signal_is_frozen(self):
        result = SignalService().emit(evaluation(EvaluationStatus.INFORMATIVE), signal_id="signal-new")
        with self.assertRaises(Exception):
            result.signal_status = SignalStatus.NEGATIVE_SIGNAL


if __name__ == "__main__":
    unittest.main()
