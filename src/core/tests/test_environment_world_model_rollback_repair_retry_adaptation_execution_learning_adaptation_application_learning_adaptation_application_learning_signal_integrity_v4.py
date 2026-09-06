"""Focused tests for M23.91 application learning signal integrity v4."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4 as Signal,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Service as SignalService,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Status as SignalStatus,
)
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
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_learning_signal_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status as IntegrityStatus,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Service as IntegrityService,
)


def evaluation(status: EvaluationStatus, outcome: OutcomeStatus = OutcomeStatus.SUCCESS) -> Evaluation:
    feedback_status = {
        OutcomeStatus.SUCCESS: FeedbackStatus.SUCCESS_FEEDBACK,
        OutcomeStatus.FAILURE: FeedbackStatus.FAILURE_FEEDBACK,
        OutcomeStatus.REJECTED: FeedbackStatus.REJECTION_FEEDBACK,
    }[outcome]
    failure_reason = "applier failed" if outcome is OutcomeStatus.FAILURE else None
    return Evaluation(
        evaluation_id="evaluation-91",
        feedback_id="feedback-91",
        feedback_source_id="feedback-source-91",
        classification_id="classification-91",
        integrity_id="integrity-90",
        application_id="application-91",
        decision_id="decision-91",
        proposal_id="proposal-91",
        outcome_id="outcome-91",
        outcome_status=outcome,
        feedback_status=feedback_status,
        confidence=0.91,
        signal_fingerprint="a" * 64,
        result_fingerprint="b" * 64,
        application_fingerprint="c" * 64,
        failure_reason=failure_reason,
        evaluation_status=status,
        reasons={"evaluation": status.value},
        lineage={"evaluation_id": "evaluation-91"},
    )


def signal(status: EvaluationStatus = EvaluationStatus.INFORMATIVE, outcome: OutcomeStatus = OutcomeStatus.SUCCESS) -> Signal:
    return SignalService().emit(evaluation(status, outcome), signal_id="signal-91")


class M23_91ApplicationLearningSignalIntegrityV4Tests(unittest.TestCase):
    def test_valid_integrity_is_emitted_for_v4_signal(self):
        result = IntegrityService().verify(signal(), integrity_id="integrity-new")
        self.assertEqual(result.status, IntegrityStatus.VALID)
        self.assertEqual(result.integrity_id, "integrity-new")
        self.assertEqual(result.signal_id, "signal-91")

    def test_fingerprint_is_deterministic_for_identical_signal(self):
        first = IntegrityService().verify(signal(), integrity_id="integrity-a")
        second = IntegrityService().verify(signal(), integrity_id="integrity-b")
        self.assertEqual(first.signal_fingerprint, second.signal_fingerprint)
        self.assertEqual(len(first.signal_fingerprint), 64)

    def test_full_v4_provenance_is_preserved(self):
        source = signal(EvaluationStatus.INFORMATIVE, OutcomeStatus.FAILURE)
        result = IntegrityService().verify(source, integrity_id="integrity-new")
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "feedback_source_id", "classification_id",
            "application_id", "decision_id", "proposal_id", "outcome_id", "confidence",
            "result_fingerprint", "application_fingerprint", "failure_reason", "evaluation_status", "signal_status",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.source_integrity_id, source.integrity_id)
        self.assertEqual(result.source_signal_fingerprint, source.signal_fingerprint)

    def test_integrity_fingerprint_covers_reasons_and_lineage(self):
        first_signal = signal()
        second_signal = Signal(
            signal_id=first_signal.signal_id,
            evaluation_id=first_signal.evaluation_id,
            feedback_id=first_signal.feedback_id,
            feedback_source_id=first_signal.feedback_source_id,
            classification_id=first_signal.classification_id,
            integrity_id=first_signal.integrity_id,
            application_id=first_signal.application_id,
            decision_id=first_signal.decision_id,
            proposal_id=first_signal.proposal_id,
            outcome_id=first_signal.outcome_id,
            outcome_status=first_signal.outcome_status,
            feedback_status=first_signal.feedback_status,
            confidence=first_signal.confidence,
            signal_fingerprint=first_signal.signal_fingerprint,
            result_fingerprint=first_signal.result_fingerprint,
            application_fingerprint=first_signal.application_fingerprint,
            failure_reason=first_signal.failure_reason,
            evaluation_status=first_signal.evaluation_status,
            signal_status=first_signal.signal_status,
            reasons={"different": True},
            lineage={"evaluation_id": first_signal.evaluation_id, "different": True},
        )
        first = IntegrityService().verify(first_signal, integrity_id="integrity-new")
        second = IntegrityService().verify(second_signal, integrity_id="integrity-new")
        self.assertNotEqual(first.signal_fingerprint, second.signal_fingerprint)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            IntegrityService().verify(object(), integrity_id="integrity-new")

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            IntegrityService().verify(signal(), integrity_id=" ")

    def test_failure_evidence_is_preserved(self):
        result = IntegrityService().verify(signal(EvaluationStatus.INFORMATIVE, OutcomeStatus.FAILURE), integrity_id="integrity-new")
        self.assertEqual(result.signal_status, SignalStatus.NEGATIVE_SIGNAL)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_ambiguous_and_non_informative_statuses_are_preserved(self):
        ambiguous = IntegrityService().verify(signal(EvaluationStatus.AMBIGUOUS), integrity_id="integrity-a")
        non_informative = IntegrityService().verify(signal(EvaluationStatus.NON_INFORMATIVE), integrity_id="integrity-b")
        self.assertEqual(ambiguous.signal_status, SignalStatus.AMBIGUOUS_SIGNAL)
        self.assertEqual(non_informative.signal_status, SignalStatus.NON_INFORMATIVE_SIGNAL)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = IntegrityService().verify(
            signal(),
            integrity_id="integrity-new",
            reasons={"nested": {"items": ["x"]}},
            lineage={"nested": {"items": ["y"]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        self.assertIsInstance(result.reasons["nested"]["items"], tuple)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["x"] = "blocked"

    def test_source_is_not_mutated(self):
        source = signal()
        before = source.__dict__.copy()
        IntegrityService().verify(source, integrity_id="integrity-new")
        self.assertEqual(source.__dict__, before)

    def test_integrity_evidence_is_advisory_only(self):
        result = IntegrityService().verify(signal(), integrity_id="integrity-new")
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.is_observational)
        for property_name in (
            "grants_authority", "authorizes_retry", "requests_retry", "updates_model", "mutates_memory",
            "mutates_policy", "mutates_persistence", "schedules_work", "executes",
        ):
            self.assertFalse(getattr(result, property_name))

    def test_integrity_evidence_is_frozen(self):
        result = IntegrityService().verify(signal(), integrity_id="integrity-new")
        with self.assertRaises(Exception):
            result.status = IntegrityStatus.INVALID


if __name__ == "__main__":
    unittest.main()
