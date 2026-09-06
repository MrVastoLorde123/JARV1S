import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Service as S,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status as I,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status as A,
)
from src.core.tests.test_environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    M23_85ApplicationLearningAdaptationApplicationV3Tests,
    _Applier,
    _FailingApplier,
)


class M23_86ApplicationLearningAdaptationApplicationIntegrityV3Tests(unittest.TestCase):
    def _proposal(self, eligible=True):
        return M23_85ApplicationLearningAdaptationApplicationV3Tests()._proposal(eligible)

    def _application(self, accept=True, eligible=True, failing=False):
        proposal = self._proposal(eligible)
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Service as DS
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Service as AS
        decision = DS().decide(proposal, decision_id="decision-86", accept=accept)
        applier = _FailingApplier() if failing else _Applier()
        return AS().apply(decision, proposal, application_id="application-86", learning_applier=applier)

    def test_applied_application_is_valid_and_fingerprinted(self):
        application = self._application()
        result = S().verify(application, integrity_id="integrity-86")
        self.assertEqual(result.integrity_status, I.VALID)
        self.assertTrue(result.application_integrity)
        self.assertEqual(len(result.application_fingerprint), 64)
        self.assertEqual(result.source_application_fingerprint, application.application_fingerprint)

    def test_rejected_application_is_valid(self):
        result = S().verify(self._application(False), integrity_id="integrity-86")
        self.assertEqual(result.integrity_status, I.VALID)
        self.assertEqual(result.application_status, A.NOT_APPLIED)

    def test_failed_application_is_valid_failure_evidence(self):
        result = S().verify(self._application(failing=True), integrity_id="integrity-86")
        self.assertEqual(result.integrity_status, I.VALID)
        self.assertEqual(result.failure_reason, "learning applier failed")

    def test_blocked_application_is_valid(self):
        result = S().verify(self._application(eligible=False), integrity_id="integrity-86")
        self.assertEqual(result.integrity_status, I.VALID)
        self.assertEqual(result.application_status, A.BLOCKED)

    def test_tampered_application_becomes_invalid(self):
        application = self._application()
        object.__setattr__(application, "failure_reason", "unexpected")
        result = S().verify(application, integrity_id="integrity-86")
        self.assertEqual(result.integrity_status, I.INVALID)
        self.assertIsNotNone(result.failure_reason)

    def test_wrong_type_fails_closed(self):
        with self.assertRaises(TypeError):
            S().verify(object(), integrity_id="integrity-86")

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            S().verify(self._application(), integrity_id="")

    def test_application_fingerprint_is_deterministic(self):
        service = S()
        first = service.verify(self._application(), integrity_id="integrity-a")
        second = service.verify(self._application(), integrity_id="integrity-b")
        self.assertEqual(first.application_fingerprint, second.application_fingerprint)

    def test_integrity_artifact_recursively_freezes_evidence(self):
        result = S().verify(
            self._application(),
            integrity_id="integrity-86",
            reasons={"nested": {"x": [1]}},
            lineage={"nested": {"y": [2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.applied_learning_update, MappingProxyType)
        self.assertIsInstance(result.application_result, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            result.lineage["nested"] = {}
        with self.assertRaises(TypeError):
            result.applied_learning_update["learning_rate"] = 1.0

    def test_integrity_is_advisory_and_preserves_source(self):
        application = self._application()
        before = application.applied_learning_update
        result = S().verify(application, integrity_id="integrity-86")
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertEqual(application.applied_learning_update, before)


if __name__ == "__main__":
    unittest.main()
