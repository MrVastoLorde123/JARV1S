import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status as E,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status as F
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status as I
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status as L,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Service as S,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status as O
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status as A
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status as D
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Service as IS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status as ISStatus,
)


class M23_81AdaptationApplicationLearningSignalIntegrityV3Tests(unittest.TestCase):
    def _evaluation(self, status):
        rej = status is E.REJECTION_EVALUATION
        fail = status is E.FAILURE_EVALUATION
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3(
            evaluation_id="evaluation-81", feedback_id="feedback-81", classification_id="classification-81", integrity_id="integrity-79",
            application_id="application-81", decision_id="decision-81", proposal_id="proposal-81", source_proposal_id="source-proposal-81",
            eligibility_id="eligibility-81", source_integrity_id="source-integrity-81", signal_id="signal-80", source_evaluation_id="evaluation-source-81",
            feedback_source_id="feedback-source-81", execution_id="execution-81", handoff_id="handoff-81", authorization_id="authorization-81",
            validation_id="validation-81", source_signal_id="source-signal-80", outcome_id="outcome-81", preparation_id="preparation-81",
            assessment_id="assessment-81", environment_id="environment-81", expected_model_id="expected-81", observed_model_id="observed-81",
            confidence=.81, signal_fingerprint="a"*64, upstream_proposal_fingerprint="b"*64, handoff_fingerprint="0"*64 if rej else "c"*64,
            result_fingerprint="0"*64 if (rej or fail) else "d"*64, application_fingerprint="e"*64,
            authority_principal_id=None if rej else "user:test", executor_id=None if rej else "executor:test",
            proposal_kind="ADAPTATION_CANDIDATE", proposal_status="PROPOSED", decision_status=D.REJECTED if rej else D.ACCEPTED,
            application_status=A.BLOCKED if rej else A.NOT_APPLIED if fail else A.APPLIED,
            integrity_status=I.VALID, outcome_status=O.REJECTED if rej else O.FAILURE if fail else O.SUCCESS,
            feedback_status=F.REJECTION_SIGNAL if rej else F.FAILURE_SIGNAL if fail else F.SUCCESS_SIGNAL,
            evaluation_status=status, failure_reason="applier failed" if fail else None,
        )

    def _signal(self, status):
        evaluation = self._evaluation(
            E.REJECTION_EVALUATION if status is L.REJECTION_SIGNAL else E.FAILURE_EVALUATION if status is L.NEGATIVE_SIGNAL else E.SUCCESS_EVALUATION
        )
        return S().emit(evaluation, signal_id="signal-81")

    def test_positive_signal_is_valid(self):
        result = IS().verify(self._signal(L.POSITIVE_SIGNAL), integrity_id="integrity-81")
        self.assertEqual(result.status, ISStatus.VALID)
        self.assertEqual(len(result.signal_fingerprint), 64)

    def test_negative_signal_is_valid(self):
        result = IS().verify(self._signal(L.NEGATIVE_SIGNAL), integrity_id="integrity-81")
        self.assertEqual(result.status, ISStatus.VALID)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_rejection_signal_is_valid(self):
        result = IS().verify(self._signal(L.REJECTION_SIGNAL), integrity_id="integrity-81")
        self.assertEqual(result.status, ISStatus.VALID)
        self.assertEqual(result.result_fingerprint, "0" * 64)
        self.assertIsNone(result.failure_reason)

    def test_fingerprint_is_deterministic(self):
        source = self._signal(L.POSITIVE_SIGNAL)
        first = IS().verify(source, integrity_id="integrity-81")
        second = IS().verify(source, integrity_id="another-integrity-81")
        self.assertEqual(first.signal_fingerprint, second.signal_fingerprint)

    def test_blank_integrity_id_is_rejected(self):
        with self.assertRaises(ValueError):
            IS().verify(self._signal(L.POSITIVE_SIGNAL), integrity_id=" ")

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            IS().verify(object(), integrity_id="integrity-81")

    def test_full_application_provenance_is_preserved(self):
        source = self._signal(L.NEGATIVE_SIGNAL)
        result = IS().verify(source, integrity_id="integrity-81")
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "application_id", "decision_id", "proposal_id",
            "source_proposal_id", "eligibility_id", "feedback_signal_id", "feedback_source_id", "source_evaluation_id", "execution_id",
            "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id",
            "expected_model_id", "observed_model_id", "proposal_kind", "proposal_status", "decision_status", "application_status",
            "integrity_status", "outcome_status", "feedback_status", "evaluation_status", "signal_status", "confidence",
            "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "application_fingerprint",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.source_integrity_id, source.integrity_id)
        self.assertEqual(result.signal_fingerprint != source.signal_fingerprint, True)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = IS().verify(
            self._signal(L.POSITIVE_SIGNAL), integrity_id="integrity-81",
            reasons={"outer": {"reason": "immutable"}}, lineage={"nested": {"x": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["x"] = "blocked"

    def test_source_is_unchanged(self):
        source = self._signal(L.NEGATIVE_SIGNAL)
        before = dict(source.lineage)
        IS().verify(source, integrity_id="integrity-81")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.signal_status, L.NEGATIVE_SIGNAL)

    def test_integrity_has_no_authority_or_mutation(self):
        result = IS().verify(self._signal(L.NEGATIVE_SIGNAL), integrity_id="integrity-81")
        self.assertTrue(result.is_advisory_only)
        self.assertTrue(result.is_observational)
        for prop in ("grants_authority", "requests_retry", "updates_model", "mutates_memory", "mutates_policy", "mutates_persistence", "schedules_work", "executes_action"):
            self.assertFalse(getattr(result, prop))


if __name__ == "__main__":
    unittest.main()
