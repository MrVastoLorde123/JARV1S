import unittest
from dataclasses import replace

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Service as TS,
)
from src.core.learning_state_transition_integrity import (
    LearningStateTransitionIntegrityService as IS,
    LearningStateTransitionIntegrityStatus as ISS,
)
from src.core.learning_state_transition_integrity_validation import (
    LearningStateTransitionIntegrityValidation as V,
    LearningStateTransitionIntegrityValidationService as VS,
    LearningStateTransitionIntegrityValidationStatus as VSStatus,
)


class LearningStateTransitionIntegrityValidationTests(unittest.TestCase):
    def _transition(self, persisted=True):
        adapter = (lambda payload: True) if persisted else None
        from src.core.tests.test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_integrity_v4 import (
            LearningStateTransitionIntegrityTests,
        )
        helper = LearningStateTransitionIntegrityTests()
        helper.setUp()
        return helper._transition(persistence_adapter=adapter)

    def _integrity(self, persisted=True):
        return IS().assess(self._transition(persisted), integrity_id="integrity-103")

    def test_persisted_valid_integrity_is_accepted(self):
        result = VS().validate(self._integrity(True), validation_id="validation-103")
        self.assertIs(result.validation_status, VSStatus.ACCEPTED)
        self.assertTrue(result.is_consumable)
        self.assertIsNone(result.failure_reason)

    def test_non_persisted_valid_integrity_is_rejected(self):
        result = VS().validate(self._integrity(False), validation_id="validation-103")
        self.assertIs(result.validation_status, VSStatus.REJECTED)
        self.assertFalse(result.is_consumable)
        self.assertIn("PERSISTED", result.failure_reason)

    def test_invalid_integrity_is_rejected(self):
        integrity = self._integrity(True)
        invalid = replace(
            integrity,
            integrity_status=ISS.INVALID,
            failure_reason="upstream integrity failed",
        )
        result = VS().validate(invalid, validation_id="validation-103")
        self.assertIs(result.validation_status, VSStatus.REJECTED)
        self.assertFalse(result.is_consumable)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            VS().validate(self._transition(True), validation_id="validation-103")

    def test_blank_validation_id_fails_closed(self):
        with self.assertRaises(ValueError):
            VS().validate(self._integrity(True), validation_id=" ")

    def test_identity_and_fingerprints_are_preserved(self):
        source = self._integrity(True)
        result = VS().validate(source, validation_id="validation-103")
        for name in (
            "integrity_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_status", "integrity_status", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence",
        ):
            self.assertEqual(getattr(result, name), getattr(source, {
                "transition_fingerprint": "computed_transition_fingerprint",
                "integrity_status": "integrity_status",
            }.get(name, name)))

    def test_result_is_immutable(self):
        result = VS().validate(self._integrity(True), validation_id="validation-103", reasons={"nested": {"items": [1]}}, lineage={"chain": ["103"]})
        with self.assertRaises(TypeError):
            result.reasons["nested"] = 1
        with self.assertRaises(TypeError):
            result.lineage["new"] = 1
        with self.assertRaises((AttributeError, TypeError)):
            result.validation_status = VSStatus.REJECTED

    def test_source_is_not_mutated(self):
        source = self._integrity(True)
        before = source.__dict__.copy()
        VS().validate(source, validation_id="validation-103")
        self.assertEqual(source.__dict__, before)

    def test_validation_is_deterministic(self):
        source = self._integrity(True)
        one = VS().validate(source, validation_id="validation-103", reasons={"b": 2, "a": 1})
        two = VS().validate(source, validation_id="validation-103", reasons={"a": 1, "b": 2})
        self.assertEqual(one, two)

    def test_validation_has_no_authority_or_side_effect_power(self):
        result = VS().validate(self._integrity(True), validation_id="validation-103")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.persists_state)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)


if __name__ == "__main__":
    unittest.main()
