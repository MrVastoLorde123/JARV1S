"""Focused tests for M23.87 learning-adaptation application outcome classification."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status,
)


class M23_87ApplicationLearningAdaptationApplicationOutcomeClassificationV3Tests(unittest.TestCase):
    def _integrity(self, *, application_status, decision_status, failure_reason=None, integrity_status=None):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3(
            integrity_id="integrity-1",
            application_id="application-1",
            decision_id="decision-1",
            proposal_id="proposal-1",
            source_proposal_id="proposal-source-1",
            eligibility_id="eligibility-1",
            eligibility_source_id="eligibility-source-1",
            integrity_source_id="integrity-upstream-1",
            signal_id="signal-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            classification_id="classification-upstream-1",
            application_source_id="application-source-1",
            source_integrity_id="source-integrity-1",
            feedback_signal_id="feedback-signal-1",
            feedback_source_id="feedback-source-1",
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
            proposal_kind="bounded-learning-adaptation",
            proposal_status="PROPOSED",
            decision_status=decision_status,
            application_status=application_status,
            applied_learning_update={"weight": 0.8} if application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED else None,
            application_result={"updated": True} if application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED else None,
            source_signal_status="POSITIVE_SIGNAL",
            confidence=0.9,
            signal_fingerprint="a" * 64,
            upstream_proposal_fingerprint="b" * 64,
            handoff_fingerprint="c" * 64,
            result_fingerprint="d" * 64,
            source_application_fingerprint="e" * 64,
            application_fingerprint="f" * 64,
            authority_principal_id=None,
            executor_id="executor-1" if application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED else None,
            failure_reason=failure_reason,
            integrity_status=integrity_status or EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status.VALID,
            reasons={"nested": {"source": ["evidence"]}},
            lineage={"chain": {"integrity": "integrity-1"}},
        )

    def test_applied_accepted_classifies_success(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-1")
        self.assertEqual(result.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS)

    def test_not_applied_accepted_with_failure_classifies_failure(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
            failure_reason="learning applier failed",
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-2")
        self.assertEqual(result.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE)
        self.assertEqual(result.failure_reason, "learning applier failed")

    def test_not_applied_rejected_classifies_rejected(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.REJECTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-3")
        self.assertEqual(result.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED)
        self.assertIsNone(result.failure_reason)

    def test_blocked_classifies_rejected(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.BLOCKED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-4")
        self.assertEqual(result.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED)

    def test_invalid_integrity_fails_closed(self):
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error):
            integrity = self._integrity(
                application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED,
                decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
                failure_reason="bad representation",
                integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status.INVALID,
            )
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-5")

    def test_provenance_and_fingerprints_are_preserved(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-6")
        for name in (
            "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id",
            "eligibility_source_id", "integrity_source_id", "signal_id", "evaluation_id", "feedback_id", "application_source_id",
            "source_integrity_id", "feedback_signal_id", "feedback_source_id", "source_evaluation_id", "execution_id", "handoff_id",
            "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id",
            "expected_model_id", "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint",
            "result_fingerprint", "source_application_fingerprint", "application_fingerprint", "proposal_kind",
        ):
            self.assertEqual(getattr(result, name), getattr(integrity, name))
        self.assertEqual(result.classification_source_id, integrity.integrity_id)

    def test_source_is_not_mutated(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        before = integrity.__dict__.copy()
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-7")
        self.assertEqual(integrity.__dict__, before)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(
            integrity,
            classification_id="class-8",
            reasons={"nested": {"items": ["x"]}},
            lineage={"nested": {"items": ["y"]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.reasons["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "value"
        with self.assertRaises(TypeError):
            result.reasons["nested"]["new"] = "value"
        self.assertIsInstance(result.lineage["nested"], MappingProxyType)

    def test_wrong_source_type_is_rejected(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service()
        with self.assertRaises(TypeError):
            service.classify(object(), classification_id="class-9")

    def test_blank_classification_id_is_rejected(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id=" ")

    def test_classification_is_advisory_and_cannot_authorize_retry_or_execute(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-10")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_feedback)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_non_failure_outcome_carries_no_failure_evidence(self):
        integrity = self._integrity(
            application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED,
            decision_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED,
        )
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service().classify(integrity, classification_id="class-11")
        self.assertNotEqual(result.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE)
        self.assertIsNone(result.failure_reason)


if __name__ == "__main__":
    unittest.main()