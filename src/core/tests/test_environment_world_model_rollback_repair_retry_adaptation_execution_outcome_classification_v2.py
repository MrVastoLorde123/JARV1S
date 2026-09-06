import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Error,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)


class M23_67AdaptationExecutionOutcomeClassificationV2Tests(unittest.TestCase):
    def _make_integrity(self, execution_status, *, integrity_status=None):
        if integrity_status is None:
            integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID
        rejected = execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2(
            integrity_id="integrity-67",
            execution_id="execution-67",
            handoff_id="handoff-67",
            authorization_id="authorization-67",
            validation_id="validation-67",
            proposal_id="proposal-67",
            eligibility_id="eligibility-67",
            source_integrity_id="integrity-66",
            signal_id="signal-67",
            evaluation_id="evaluation-67",
            feedback_id="feedback-67",
            outcome_id="outcome-67",
            preparation_id="preparation-67",
            decision_id="decision-67",
            source_proposal_id="source-proposal-67",
            assessment_id="assessment-67",
            environment_id="env-67",
            expected_model_id="expected-67",
            observed_model_id="observed-67",
            eligibility_status=EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE,
            proposal_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED if rejected else EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED),
            validation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID,
            authorization_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED if rejected else EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED),
            handoff_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED if rejected else EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY),
            execution_status=execution_status,
            confidence=0.91,
            signal_fingerprint="a" * 64,
            proposal_kind="world_model_patch",
            proposal_fingerprint="b" * 64,
            handoff_fingerprint=("0" * 64 if rejected else "c" * 64),
            authority_principal_id=(None if rejected else "user:test"),
            authority_kind=(None if rejected else EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER),
            authorization_scope=(None if rejected else {"proposal_id": "proposal-67", "proposal_fingerprint": "b" * 64}),
            executor_id=(None if rejected else "executor:test"),
            observed_result=(None if execution_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED else {"changed": True}),
            result_fingerprint=(("0" * 64) if execution_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED else "d" * 64),
            failure_reason=("rejected" if rejected else ("executor failed" if execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED else None)),
            integrity_status=integrity_status,
            reasons={"reason": "test"},
            lineage={"nested": {"id": "67"}},
        )

    def test_completed_becomes_success(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED),
            classification_id="classification-67",
        )
        self.assertEqual(result.classification_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS)

    def test_failed_becomes_failure(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED),
            classification_id="classification-67",
        )
        self.assertEqual(result.classification_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE)

    def test_rejected_stays_rejected(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED),
            classification_id="classification-67",
        )
        self.assertEqual(result.classification_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED)
        self.assertIsNone(result.authority_principal_id)

    def test_invalid_integrity_cannot_be_classified(self):
        integrity = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED)
        object.__setattr__(integrity, "integrity_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID)
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Error):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
                integrity,
                classification_id="classification-67",
            )

    def test_blank_classification_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
                self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED),
                classification_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
                object(),
                classification_id="classification-67",
            )

    def test_full_provenance_and_fingerprints_are_preserved(self):
        source = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            source,
            classification_id="classification-67",
        )
        self.assertEqual(result.integrity_id, source.integrity_id)
        self.assertEqual(result.execution_id, source.execution_id)
        self.assertEqual(result.proposal_fingerprint, source.proposal_fingerprint)
        self.assertEqual(result.handoff_fingerprint, source.handoff_fingerprint)
        self.assertEqual(result.result_fingerprint, source.result_fingerprint)

    def test_source_is_unchanged(self):
        source = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            source,
            classification_id="classification-67",
        )
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID)

    def test_reasons_and_lineage_are_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED),
            classification_id="classification-67",
            reasons={"outer": "reason"},
            lineage={"nested": {"x": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"

    def test_classification_does_not_create_learning_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED),
            classification_id="classification-67",
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)

    def test_classification_does_not_grant_authority_or_schedule(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service().classify(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED),
            classification_id="classification-67",
        )
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_memory)


if __name__ == "__main__":
    unittest.main()
