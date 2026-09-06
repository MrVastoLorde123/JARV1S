import unittest

from src.core.learning_state_consumption_request import (
    LearningStateConsumptionRequestService as S,
    LearningStateConsumptionRequestStatus as RS,
)
from src.core.learning_state_transition_integrity_validation import (
    LearningStateTransitionIntegrityValidation,
    LearningStateTransitionIntegrityValidationStatus as VS,
)
from src.core.learning_state_transition_integrity import LearningStateTransitionIntegrityStatus as IS
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TS,
)


class LearningStateConsumptionRequestTests(unittest.TestCase):
    def _validation(self, status=VS.ACCEPTED):
        return LearningStateTransitionIntegrityValidation(
            validation_id="validation-103",
            integrity_id="integrity-99",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="skill.demo",
            transition_status=TS.PERSISTED,
            integrity_status=IS.VALID,
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            validation_status=status,
            failure_reason=None if status is VS.ACCEPTED else "blocked",
            reasons={"nested": {"value": 1}},
            lineage={"chain": ["103", "99"]},
        )

    def test_accepted_validation_forms_ready_request(self):
        result = S().request(self._validation(), request_id="request-104")
        self.assertIs(result.request_status, RS.READY)
        self.assertTrue(result.is_readable)

    def test_rejected_validation_forms_rejected_request(self):
        result = S().request(self._validation(VS.REJECTED), request_id="request-104")
        self.assertIs(result.request_status, RS.REJECTED)
        self.assertFalse(result.is_readable)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            S().request(object(), request_id="request-104")

    def test_blank_request_id_fails_closed(self):
        with self.assertRaises(ValueError):
            S().request(self._validation(), request_id=" ")

    def test_identity_and_fingerprint_provenance_are_preserved(self):
        source = self._validation()
        result = S().request(source, request_id="request-104")
        for name in (
            "validation_id", "integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "confidence",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_request_is_deterministic(self):
        source = self._validation()
        one = S().request(source, request_id="request-104")
        two = S().request(source, request_id="request-104")
        self.assertEqual(one, two)

    def test_nested_reasons_and_lineage_are_immutable(self):
        result = S().request(self._validation(), request_id="request-104")
        with self.assertRaises(TypeError):
            result.reasons["nested"] = 1
        with self.assertRaises(TypeError):
            result.lineage["new"] = 1

    def test_source_is_not_mutated(self):
        source = self._validation()
        before = source
        S().request(source, request_id="request-104")
        self.assertEqual(source, before)

    def test_request_does_not_read_or_write_durable_state(self):
        result = S().request(self._validation(), request_id="request-104")
        self.assertFalse(result.reads_durable_state)
        self.assertFalse(result.writes_durable_state)

    def test_request_has_no_learning_or_authority_power(self):
        result = S().request(self._validation(), request_id="request-104")
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.executes_action)


if __name__ == "__main__":
    unittest.main()
