import unittest

from src.core.learning_state_consumption_read import (
    LearningStateConsumptionRead,
    LearningStateConsumptionReadService as S,
    LearningStateConsumptionReadStatus as RS,
)
from src.core.learning_state_consumption_request import (
    LearningStateConsumptionRequest,
    LearningStateConsumptionRequestStatus as Q,
    LearningStateConsumptionRequestService as QS,
)
from src.core.learning_state_transition_integrity_validation import (
    LearningStateTransitionIntegrityValidation,
    LearningStateTransitionIntegrityValidationStatus as VS,
)


class LearningStateConsumptionReadTests(unittest.TestCase):
    def _validation(self, status=VS.ACCEPTED):
        return LearningStateTransitionIntegrityValidation(
            validation_id="validation-103", integrity_id="integrity-99", transition_id="transition-98",
            evidence_id="evidence-97", application_id="application-96", state_key="skill.demo",
            transition_status=__import__("src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4", fromlist=["X"]).EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status.PERSISTED,
            integrity_status=__import__("src.core.learning_state_transition_integrity", fromlist=["X"]).LearningStateTransitionIntegrityStatus.VALID,
            transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64, confidence=0.91, validation_status=status,
            failure_reason=None if status is VS.ACCEPTED else "blocked", reasons={"v": 1}, lineage={"v": 1},
        )

    def _request(self, status=VS.ACCEPTED):
        return QS().request(self._validation(status), request_id="request-104")

    def test_ready_request_can_be_consumed(self):
        calls=[]
        result=S().consume(self._request(), read_id="read-105", reader=lambda meta: calls.append(meta) or {"value": 42})
        self.assertIs(result.read_status, RS.CONSUMED)
        self.assertEqual(result.state["value"], 42)
        self.assertEqual(len(calls), 1)

    def test_rejected_request_is_not_read(self):
        calls=[]
        result=S().consume(self._request(VS.REJECTED), read_id="read-105", reader=lambda meta: calls.append(meta) or {"value": 42})
        self.assertIs(result.read_status, RS.REJECTED)
        self.assertEqual(calls, [])

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            S().consume(self._validation(), read_id="read-105", reader=lambda meta: {})

    def test_blank_read_id_fails_closed(self):
        with self.assertRaises(ValueError):
            S().consume(self._request(), read_id=" ", reader=lambda meta: {})

    def test_reader_receives_only_bounded_metadata(self):
        seen=[]
        S().consume(self._request(), read_id="read-105", reader=lambda meta: seen.append(meta) or {})
        self.assertEqual(set(seen[0]), {"request_id", "validation_id", "integrity_id", "transition_id", "state_key"})

    def test_reader_exception_rejects_without_retry(self):
        calls=[]
        def reader(meta):
            calls.append(1)
            raise RuntimeError("boom")
        result=S().consume(self._request(), read_id="read-105", reader=reader)
        self.assertIs(result.read_status, RS.REJECTED)
        self.assertEqual(len(calls), 1)

    def test_non_mapping_reader_result_rejects(self):
        result=S().consume(self._request(), read_id="read-105", reader=lambda meta: [1, 2])
        self.assertIs(result.read_status, RS.REJECTED)
        self.assertIsNone(result.state)

    def test_nested_state_is_immutable(self):
        result=S().consume(self._request(), read_id="read-105", reader=lambda meta: {"nested": {"items": [1]}})
        with self.assertRaises(TypeError):
            result.state["nested"]["items"] = 2

    def test_source_request_is_not_mutated(self):
        source=self._request()
        before=source.__dict__.copy()
        S().consume(source, read_id="read-105", reader=lambda meta: {"value": 1})
        self.assertEqual(source.__dict__, before)

    def test_identity_and_fingerprints_are_preserved(self):
        source=self._request()
        result=S().consume(source, read_id="read-105", reader=lambda meta: {"value": 1})
        for name in ("request_id","validation_id","integrity_id","transition_id","evidence_id","application_id","state_key","transition_fingerprint","source_application_fingerprint","computed_application_fingerprint","confidence"):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_result_declares_no_write_or_learning_power(self):
        result=S().consume(self._request(), read_id="read-105", reader=lambda meta: {"value": 1})
        self.assertTrue(result.read_only)
        self.assertFalse(result.writes_durable_state)
        self.assertFalse(result.retries)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.executes_action)

    def test_result_is_immutable(self):
        result=S().consume(self._request(), read_id="read-105", reader=lambda meta: {"value": 1})
        with self.assertRaises((AttributeError, TypeError)):
            result.read_id="other"

    def test_read_is_deterministic_for_equivalent_requests(self):
        one=S().consume(self._request(), read_id="read-105", reader=lambda meta: {"value": 1})
        two=S().consume(self._request(), read_id="read-105", reader=lambda meta: {"value": 1})
        self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()
