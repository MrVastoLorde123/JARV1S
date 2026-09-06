"""Focused tests for M23.92 application learning eligibility v4."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4 as Integrity,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status as IntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4 as Signal,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Service as SignalService,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status as OutcomeStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status as FeedbackStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3 as Evaluation,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status as EvaluationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4 as Eligibility,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Service as EligibilityService,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status as EligibilityStatus,
)


def evaluation(status: EvaluationStatus, outcome: OutcomeStatus = OutcomeStatus.SUCCESS) -> Evaluation:
    feedback_status = {
        OutcomeStatus.SUCCESS: FeedbackStatus.SUCCESS_FEEDBACK,
        OutcomeStatus.FAILURE: FeedbackStatus.FAILURE_FEEDBACK,
        OutcomeStatus.REJECTED: FeedbackStatus.REJECTION_FEEDBACK,
    }[outcome]
    failure_reason = "applier failed" if outcome is OutcomeStatus.FAILURE else None
    return Evaluation(
        evaluation_id="evaluation-92",
        feedback_id="feedback-92",
        feedback_source_id="feedback-source-92",
        classification_id="classification-92",
        integrity_id="integrity-91",
        application_id="application-92",
        decision_id="decision-92",
        proposal_id="proposal-92",
        outcome_id="outcome-92",
        outcome_status=outcome,
        feedback_status=feedback_status,
        confidence=0.91,
        signal_fingerprint="a" * 64,
        result_fingerprint="b" * 64,
        application_fingerprint="c" * 64,
        failure_reason=failure_reason,
        evaluation_status=status,
        reasons={"evaluation": status.value},
        lineage={"evaluation_id": "evaluation-92"},
    )


def signal(status: EvaluationStatus = EvaluationStatus.INFORMATIVE, outcome: OutcomeStatus = OutcomeStatus.SUCCESS) -> Signal:
    return SignalService().emit(evaluation(status, outcome), signal_id="signal-92")


def integrity(status: IntegrityStatus = IntegrityStatus.VALID) -> Integrity:
    source = signal()
    return Integrity(
        integrity_id="integrity-91",
        signal_id=source.signal_id,
        evaluation_id=source.evaluation_id,
        feedback_id=source.feedback_id,
        feedback_source_id=source.feedback_source_id,
        classification_id=source.classification_id,
        source_integrity_id=source.integrity_id,
        application_id=source.application_id,
        decision_id=source.decision_id,
        proposal_id=source.proposal_id,
        outcome_id=source.outcome_id,
        outcome_status=source.outcome_status,
        feedback_status=source.feedback_status,
        confidence=source.confidence,
        signal_fingerprint="d" * 64,
        result_fingerprint=source.result_fingerprint,
        application_fingerprint=source.application_fingerprint,
        failure_reason=source.failure_reason,
        evaluation_status=source.evaluation_status,
        signal_status=source.signal_status,
        status=status,
        source_signal_fingerprint=source.signal_fingerprint,
        reasons={"integrity": status.value},
        lineage={"integrity_id": "integrity-91"},
    )


class M23_92ApplicationLearningEligibilityV4Tests(unittest.TestCase):
    def test_valid_integrity_maps_to_eligible(self):
        result = EligibilityService().assess(integrity(), eligibility_id="eligibility-new")
        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)

    def test_invalid_integrity_maps_to_ineligible(self):
        result = EligibilityService().assess(integrity(IntegrityStatus.INVALID), eligibility_id="eligibility-new")
        self.assertEqual(result.status, EligibilityStatus.INELIGIBLE)

    def test_new_eligibility_identity_and_integrity_provenance_are_preserved(self):
        source = integrity()
        result = EligibilityService().assess(source, eligibility_id="eligibility-new")
        self.assertEqual(result.eligibility_id, "eligibility-new")
        self.assertEqual(result.integrity_id, source.integrity_id)
        self.assertEqual(result.signal_id, source.signal_id)
        self.assertEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.source_integrity_id, source.source_integrity_id)

    def test_full_v4_provenance_is_preserved(self):
        source = integrity()
        result = EligibilityService().assess(source, eligibility_id="eligibility-new")
        for name in (
            "feedback_id", "feedback_source_id", "classification_id", "application_id", "decision_id",
            "proposal_id", "outcome_id", "outcome_status", "feedback_status", "confidence",
            "signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint",
            "failure_reason", "evaluation_status", "signal_status",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_failure_evidence_is_preserved(self):
        source_signal = signal(EvaluationStatus.INFORMATIVE, OutcomeStatus.FAILURE)
        source = IntegrityService().verify(source_signal, integrity_id="integrity-91")
        result = EligibilityService().assess(source, eligibility_id="eligibility-new")
        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_rejection_evidence_is_preserved(self):
        source_signal = signal(EvaluationStatus.INFORMATIVE, OutcomeStatus.REJECTED)
        source = IntegrityService().verify(source_signal, integrity_id="integrity-91")
        result = EligibilityService().assess(source, eligibility_id="eligibility-new")
        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.outcome_status, OutcomeStatus.REJECTED)

    def test_ambiguous_and_non_informative_signal_state_is_preserved(self):
        ambiguous = IntegrityService().verify(signal(EvaluationStatus.AMBIGUOUS), integrity_id="integrity-a")
        non_informative = IntegrityService().verify(signal(EvaluationStatus.NON_INFORMATIVE), integrity_id="integrity-b")
        self.assertEqual(EligibilityService().assess(ambiguous, eligibility_id="eligibility-a").status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(EligibilityService().assess(non_informative, eligibility_id="eligibility-b").status, EligibilityStatus.ELIGIBLE)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EligibilityService().assess(object(), eligibility_id="eligibility-new")

    def test_blank_eligibility_id_fails_closed(self):
        with self.assertRaises(ValueError):
            EligibilityService().assess(integrity(), eligibility_id=" ")

    def test_status_mismatch_is_rejected(self):
        source = integrity()
        with self.assertRaises(ValueError):
            Eligibility(
                eligibility_id="eligibility-new",
                integrity_id=source.integrity_id,
                signal_id=source.signal_id,
                evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id,
                feedback_source_id=source.feedback_source_id,
                classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id,
                application_id=source.application_id,
                decision_id=source.decision_id,
                proposal_id=source.proposal_id,
                outcome_id=source.outcome_id,
                outcome_status=source.outcome_status,
                feedback_status=source.feedback_status,
                confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint,
                source_signal_fingerprint=source.source_signal_fingerprint,
                result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint,
                failure_reason=source.failure_reason,
                evaluation_status=source.evaluation_status,
                signal_status=source.signal_status,
                integrity_status=IntegrityStatus.VALID,
                status=EligibilityStatus.INELIGIBLE,
            )

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = EligibilityService().assess(
            integrity(),
            eligibility_id="eligibility-new",
            reasons={"nested": {"items": ["x"]}},
            lineage={"nested": {"items": ["y"]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        self.assertIsInstance(result.reasons["nested"]["items"], tuple)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["blocked"] = True

    def test_source_is_not_mutated(self):
        source = integrity()
        before = source.__dict__.copy()
        EligibilityService().assess(source, eligibility_id="eligibility-new")
        self.assertEqual(source.__dict__, before)

    def test_eligibility_is_advisory_only(self):
        result = EligibilityService().assess(integrity(), eligibility_id="eligibility-new")
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.is_observational)
        for property_name in (
            "is_learning", "permits_learning", "grants_authority", "authorizes_retry", "requests_retry",
            "updates_model", "mutates_memory", "mutates_policy", "mutates_persistence", "schedules_work", "executes",
        ):
            self.assertFalse(getattr(result, property_name))

    def test_eligibility_is_frozen(self):
        result = EligibilityService().assess(integrity(), eligibility_id="eligibility-new")
        with self.assertRaises(Exception):
            result.status = EligibilityStatus.INELIGIBLE


if __name__ == "__main__":
    unittest.main()
