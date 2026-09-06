"""Focused tests for M23.88 application-learning adaptation application outcome feedback."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status,
)


class M23_88ApplicationLearningAdaptationApplicationOutcomeFeedbackV3Tests(unittest.TestCase):
    def _classification(self, *, outcome, failure_reason=None):
        states = {
            "success": (
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS,
            ),
            "failure": (
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE,
            ),
            "rejected": (
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.REJECTED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED,
            ),
        }
        application_status, decision_status, outcome_status = states[outcome]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3(
            classification_id="classification-1",
            integrity_id="integrity-1",
            application_id="application-1",
            decision_id="decision-1",
            proposal_id="proposal-1",
            source_proposal_id="proposal-source-1",
            eligibility_id="eligibility-1",
            eligibility_source_id="eligibility-source-1",
            integrity_source_id="integrity-source-1",
            signal_id="signal-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-upstream-1",
            classification_source_id="integrity-1",
            application_source_id="application-source-1",
            source_integrity_id="source-integrity-1",
            feedback_signal_id="feedback-signal-1",
            feedback_source_id="source-feedback-1",
            source_evaluation_id="source-evaluation-1",
            execution_id="execution-1",
            handoff_id="handoff-1",
            authorization_id="authorization-1",
            validation_id="validation-1",
            source_signal_id="source-signal-1",
            outcome_id="outcome-1",
            preparation_id="preparation-1",
            assessment_id="assessment-1",
            environment_id="environment-1",
            expected_model_id="expected-model-1",
            observed_model_id="observed-model-1",
            confidence=0.9,
            signal_fingerprint="a" * 64,
            upstream_proposal_fingerprint="b" * 64,
            handoff_fingerprint="c" * 64,
            result_fingerprint="d" * 64,
            source_application_fingerprint="e" * 64,
            application_fingerprint="f" * 64,
            authority_principal_id=None,
            executor_id="executor-1" if application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED else None,
            proposal_kind="bounded-learning-adaptation",
            proposal_status="PROPOSED",
            decision_status=decision_status,
            application_status=application_status,
            integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status.VALID,
            outcome_status=outcome_status,
            failure_reason=failure_reason,
            reasons={"nested": {"source": ["evidence"]}},
            lineage={"chain": {"classification": "classification-1"}},
        )

    def test_success_maps_to_success_feedback(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="success"), feedback_id="feedback-1")
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK)
        self.assertIsNone(result.failure_reason)

    def test_failure_maps_to_failure_feedback_and_preserves_reason(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="failure", failure_reason="learning applier failed"), feedback_id="feedback-2")
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK)
        self.assertEqual(result.failure_reason, "learning applier failed")

    def test_rejected_maps_to_rejection_feedback(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="rejected"), feedback_id="feedback-3")
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.REJECTION_FEEDBACK)
        self.assertIsNone(result.failure_reason)

    def test_failure_feedback_requires_failure_evidence(self):
        source = self._classification(outcome="failure", failure_reason="source failure")
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3(
                **{
                    **source.__dict__,
                    "feedback_id": "feedback-4",
                    "feedback_source_id": "classification-1",
                    "feedback_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK,
                    "failure_reason": None,
                }
            )

    def test_non_failure_feedback_carries_no_failure_evidence(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="success"), feedback_id="feedback-5")
        self.assertIsNone(result.failure_reason)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3(
                **{
                    **self._classification(outcome="success").__dict__,
                    "feedback_id": "feedback-5b",
                    "feedback_source_id": "classification-1",
                    "feedback_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK,
                    "failure_reason": "unexpected",
                }
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(object(), feedback_id="feedback-6")

    def test_blank_feedback_id_fails_closed(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="success"), feedback_id=" ")

    def test_provenance_and_fingerprints_are_preserved(self):
        classification = self._classification(outcome="success")
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(classification, feedback_id="feedback-7")
        for name in (
            "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id",
            "eligibility_source_id", "integrity_source_id", "signal_id", "evaluation_id", "classification_source_id",
            "application_source_id", "source_integrity_id", "feedback_signal_id", "source_evaluation_id", "execution_id", "handoff_id",
            "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id", "expected_model_id",
            "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
            "source_application_fingerprint", "application_fingerprint", "proposal_kind",
        ):
            self.assertEqual(getattr(result, name), getattr(classification, name))
        self.assertEqual(result.feedback_id, "feedback-7")
        self.assertNotEqual(result.feedback_id, classification.feedback_id)
        self.assertEqual(result.feedback_source_id, classification.classification_id)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(
            self._classification(outcome="success"), feedback_id="feedback-8", reasons={"nested": {"items": ["x"]}}, lineage={"nested": {"items": ["y"]}}
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        self.assertIsInstance(result.reasons["nested"]["items"], tuple)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["new"] = "value"
        self.assertIsInstance(result.lineage["nested"], MappingProxyType)

    def test_source_is_not_mutated(self):
        classification = self._classification(outcome="failure", failure_reason="x")
        before = classification.__dict__.copy()
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(classification, feedback_id="feedback-9")
        self.assertEqual(classification.__dict__, before)

    def test_feedback_is_advisory_only(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service().record(self._classification(outcome="success"), feedback_id="feedback-10")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_wrong_feedback_status_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3(
                **{
                    **self._classification(outcome="success").__dict__,
                    "feedback_id": "feedback-11",
                    "feedback_source_id": "classification-1",
                    "feedback_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK,
                }
            )

    def test_wrong_integrity_status_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3(
                **{
                    **self._classification(outcome="success").__dict__,
                    "feedback_id": "feedback-12",
                    "feedback_source_id": "classification-1",
                    "feedback_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK,
                    "integrity_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status.INVALID,
                }
            )


if __name__ == "__main__":
    unittest.main()
