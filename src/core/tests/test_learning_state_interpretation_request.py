import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TS
from src.core.learning_state_transition_integrity import LearningStateTransitionIntegrityStatus as IS
from src.core.learning_state_transition_integrity_validation import LearningStateTransitionIntegrityValidation, LearningStateTransitionIntegrityValidationStatus as IVS
from src.core.learning_state_consumption_read_validation import LearningStateConsumptionReadValidationService as RVS
from src.core.learning_state_consumption_read import LearningStateConsumptionReadService as RCS
from src.core.learning_state_consumption_request import LearningStateConsumptionRequestService as QRS
from src.core.learning_state_interpretation_request import LearningStateInterpretationRequestService as S, LearningStateInterpretationRequestStatus as RS


class LearningStateInterpretationRequestTests(unittest.TestCase):
    def _validation(self, status=IVS.ACCEPTED):
        transition_fingerprint="a" * 64
        return LearningStateTransitionIntegrityValidation(validation_id="validation-103", integrity_id="integrity-99", transition_id="transition-98", evidence_id="evidence-97", application_id="application-96", state_key="skill.demo", transition_status=TS.PERSISTED, integrity_status=IS.VALID, transition_fingerprint=transition_fingerprint, source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91, validation_status=status, failure_reason=None if status is IVS.ACCEPTED else "blocked", reasons={"v": 1}, lineage={"v": 1})

    def _read_validation(self, status=IVS.ACCEPTED):
        request=QRS().request(self._validation(), request_id="request-104")
        read=RCS().consume(request, read_id="read-105", reader=lambda meta: {"nested":{"items":[1,2]},"value":42})
        if status is IVS.REJECTED:
            read=RCS().consume(QRS().request(self._validation(IVS.REJECTED), request_id="request-104"), read_id="read-105", reader=lambda meta: {"value":42})
        return RVS().validate(read, validation_id="validation-106")

    def test_accepted_validation_forms_ready_request(self):
        result=S().request(self._read_validation(), request_id="interpret-107")
        self.assertIs(result.request_status, RS.READY)
        self.assertTrue(result.is_ready)

    def test_rejected_validation_forms_rejected_request(self):
        result=S().request(self._read_validation(IVS.REJECTED), request_id="interpret-107")
        self.assertIs(result.request_status, RS.REJECTED)
        self.assertFalse(result.is_ready)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError): S().request(object(), request_id="interpret-107")

    def test_blank_request_id_fails_closed(self):
        with self.assertRaises(ValueError): S().request(self._read_validation(), request_id=" ")

    def test_provenance_and_fingerprints_are_preserved(self):
        source=self._read_validation(); result=S().request(source, request_id="interpret-107")
        for name in ("read_id","read_validation_id","consumption_request_id","source_validation_id","integrity_id","transition_id","evidence_id","application_id","state_key","transition_fingerprint","source_application_fingerprint","computed_application_fingerprint","confidence"):
            expected_name = {"read_validation_id": "validation_id", "consumption_request_id": "request_id"}.get(name, name)
            self.assertEqual(getattr(result, name), getattr(source, expected_name))
        self.assertEqual(result.request_id, "interpret-107")
        self.assertEqual(result.consumption_request_id, source.request_id)

    def test_state_is_preserved_and_recursively_immutable(self):
        source=self._read_validation(); result=S().request(source, request_id="interpret-107")
        self.assertEqual(result.state["nested"]["items"], (1,2))
        with self.assertRaises(TypeError): result.state["nested"] = 1

    def test_reasons_and_lineage_are_immutable(self):
        result=S().request(self._read_validation(), request_id="interpret-107", reasons={"nested":{"v":1}}, lineage={"nested":{"v":1}})
        with self.assertRaises(TypeError): result.reasons["nested"] = 1
        with self.assertRaises(TypeError): result.lineage["nested"] = 1

    def test_source_validation_is_not_mutated(self):
        source=self._read_validation(); before=source; S().request(source, request_id="interpret-107"); self.assertEqual(source, before)

    def test_request_does_not_interpret_state(self):
        result=S().request(self._read_validation(), request_id="interpret-107")
        self.assertFalse(result.interprets_state)
        self.assertEqual(result.state["value"], 42)

    def test_request_has_no_truth_learning_or_authority_power(self):
        result=S().request(self._read_validation(), request_id="interpret-107")
        self.assertFalse(result.establishes_truth); self.assertFalse(result.establishes_correctness); self.assertFalse(result.invokes_interpreter); self.assertFalse(result.invokes_learner); self.assertFalse(result.updates_model); self.assertFalse(result.mutates_memory); self.assertFalse(result.mutates_policy); self.assertFalse(result.grants_authority); self.assertFalse(result.executes_action)

    def test_request_is_deterministic(self):
        source=self._read_validation(); self.assertEqual(S().request(source, request_id="interpret-107"), S().request(source, request_id="interpret-107"))

    def test_result_is_immutable(self):
        result=S().request(self._read_validation(), request_id="interpret-107")
        with self.assertRaises((AttributeError, TypeError)): result.request_id="other"

if __name__ == "__main__": unittest.main()
