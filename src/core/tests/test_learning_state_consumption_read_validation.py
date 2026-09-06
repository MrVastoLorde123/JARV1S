import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TS,
)
from src.core.learning_state_consumption_read import (
    LearningStateConsumptionReadService as RS,
    LearningStateConsumptionReadStatus as RStatus,
)
from src.core.learning_state_consumption_request import LearningStateConsumptionRequestService as QS
from src.core.learning_state_consumption_read_validation import (
    LearningStateConsumptionReadValidation,
    LearningStateConsumptionReadValidationService as VS,
    LearningStateConsumptionReadValidationStatus as VStatus,
)
from src.core.learning_state_transition_integrity import LearningStateTransitionIntegrityStatus as IS
from src.core.learning_state_transition_integrity_validation import (
    LearningStateTransitionIntegrityValidation,
    LearningStateTransitionIntegrityValidationStatus as IVStatus,
)


class LearningStateConsumptionReadValidationTests(unittest.TestCase):
    def _validation(self, status=IVStatus.ACCEPTED):
        return LearningStateTransitionIntegrityValidation(
            validation_id="validation-103", integrity_id="integrity-99", transition_id="transition-98",
            evidence_id="evidence-97", application_id="application-96", state_key="skill.demo",
            transition_status=TS.PERSISTED, integrity_status=IS.VALID,
            transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64, confidence=0.91,
            validation_status=status, failure_reason=None if status is IVStatus.ACCEPTED else "blocked",
            reasons={"v": 1}, lineage={"chain": ["103", "99"]},
        )

    def _request(self, status=IVStatus.ACCEPTED):
        return QS().request(self._validation(status), request_id="request-104")

    def _read(self, request=None):
        request = self._request() if request is None else request
        return RS().consume(request, read_id="read-105", reader=lambda meta: {"nested": {"value": 42}})

    def test_consumed_mapping_read_is_accepted(self):
        result = VS().validate(self._read(), validation_id="validation-106")
        self.assertIs(result.validation_status, VStatus.ACCEPTED)

    def test_rejected_read_is_rejected(self):
        result = VS().validate(
            RS().consume(self._request(), read_id="read-105", reader=lambda meta: (_ for _ in ()).throw(RuntimeError("boom"))),
            validation_id="validation-106",
        )
        self.assertIs(result.validation_status, VStatus.REJECTED)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            VS().validate(object(), validation_id="validation-106")

    def test_blank_validation_id_fails_closed(self):
        with self.assertRaises(ValueError):
            VS().validate(self._read(), validation_id=" ")

    def test_read_provenance_and_fingerprints_are_preserved(self):
        source = self._read()
        result = VS().validate(source, validation_id="validation-106")
        for name in (
            "read_id", "request_id", "validation_id", "integrity_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence",
        ):
            expected = source.validation_id if name == "validation_id" else getattr(source, name)
            self.assertEqual(getattr(result, "source_validation_id" if name == "validation_id" else name), expected)

    def test_consumed_state_is_preserved_and_immutable(self):
        result = VS().validate(self._read(), validation_id="validation-106")
        self.assertEqual(result.state["nested"]["value"], 42)
        with self.assertRaises(TypeError):
            result.state["nested"]["value"] = 7

    def test_source_read_is_not_mutated(self):
        source = self._read()
        before = source
        result = VS().validate(source, validation_id="validation-106")
        self.assertEqual(source, before)
        self.assertEqual(result.state, source.state)

    def test_rejected_request_cannot_produce_consumed_validation(self):
        read = RS().consume(
            self._request(IVStatus.REJECTED), read_id="read-105", reader=lambda meta: {"value": 1}
        )
        result = VS().validate(read, validation_id="validation-106")
        self.assertIs(read.read_status, RStatus.REJECTED)
        self.assertIs(result.validation_status, VStatus.REJECTED)

    def test_validation_does_not_establish_truth_or_correctness(self):
        result = VS().validate(self._read(), validation_id="validation-106")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)

    def test_validation_has_no_learning_or_authority_power(self):
        result = VS().validate(self._read(), validation_id="validation-106")
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_nested_reasons_and_lineage_are_immutable(self):
        result = VS().validate(self._read(), validation_id="validation-106", reasons={"nested": {"x": 1}}, lineage={"chain": [{"id": "105"}]})
        with self.assertRaises(TypeError):
            result.reasons["nested"] = 2
        with self.assertRaises(TypeError):
            result.lineage["chain"] = ()

    def test_validation_is_deterministic(self):
        source = self._read()
        one = VS().validate(source, validation_id="validation-106")
        two = VS().validate(source, validation_id="validation-106")
        self.assertEqual(one, two)

    def test_validation_result_is_immutable(self):
        result = VS().validate(self._read(), validation_id="validation-106")
        with self.assertRaises((AttributeError, TypeError)):
            result.validation_id = "other"


if __name__ == "__main__":
    unittest.main()
