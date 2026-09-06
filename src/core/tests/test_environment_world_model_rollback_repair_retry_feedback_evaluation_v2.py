import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
)


class M23_57FeedbackEvaluationV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.success = EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
            feedback_id="feedback1",
            outcome_id="outcome1",
            integrity_id="integrity1",
            execution_id="execution1",
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_decision_id="decision-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id=None,
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status=EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS,
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL,
            result_fingerprint="fp123",
            failure_reason=None,
            worker_id="worker1",
            reasons={"status": "success"},
            lineage={"nested": {"source": "outcome1"}},
        )
        self.failure = EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
            feedback_id="feedback2",
            outcome_id="outcome2",
            integrity_id="integrity2",
            execution_id="execution2",
            preparation_id="preparation1",
            decision_id="decision1",
            integrity_decision_id="decision-integrity1",
            proposal_id="proposal1",
            assessment_id="assessment1",
            evaluation_id=None,
            environment_id="env1",
            expected_model_id="expected",
            observed_model_id="observed",
            outcome_status=EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE,
            feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL,
            result_fingerprint=None,
            failure_reason="provider unavailable",
            worker_id="worker1",
        )
        self.service = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service()

    def test_success_feedback_becomes_success_evaluation_and_preserves_v2_chain(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation1")
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        self.assertEqual(result.result_fingerprint, "fp123")
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.integrity_id, "integrity1")
        self.assertEqual(result.decision_id, "decision1")
        self.assertEqual(result.proposal_id, "proposal1")

    def test_failure_feedback_becomes_failure_evaluation_and_preserves_reason(self) -> None:
        result = self.service.evaluate(self.failure, evaluation_id="evaluation2")
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION)
        self.assertEqual(result.failure_reason, "provider unavailable")
        self.assertIsNone(result.result_fingerprint)
        self.assertEqual(result.feedback_id, "feedback2")
        self.assertEqual(result.outcome_id, "outcome2")

    def test_custom_confidence_is_bounded(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation3", confidence=0.75)
        self.assertEqual(result.confidence, 0.75)
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id="evaluation4", confidence=1.1)
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id="evaluation5", confidence=-0.1)
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id="evaluation6", confidence=True)

    def test_evaluation_is_immutable_and_advisory(self) -> None:
        result = self.service.evaluate(self.success, evaluation_id="evaluation7")
        with self.assertRaises(AttributeError):
            result.evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION
        self.assertTrue(result.is_observational)
        self.assertFalse(result.recommends_retry)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)

    def test_nested_lineage_is_frozen_and_source_feedback_is_unchanged(self) -> None:
        before = self.success.lineage
        result = self.service.evaluate(
            self.success,
            evaluation_id="evaluation8",
            reasons={"cause": "validated"},
            lineage={"nested": {"source": "feedback1"}},
        )
        self.assertEqual(result.reasons["cause"], "validated")
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["nested"]["source"] = "changed"
        self.assertEqual(self.success.lineage, before)

    def test_evaluation_id_is_required_and_wrong_type_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.service.evaluate(self.success, evaluation_id=" ")
        with self.assertRaises(TypeError):
            self.service.evaluate(object(), evaluation_id="evaluation9")

    def test_constructor_rejects_mismatched_status(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2(
                evaluation_id="bad1",
                feedback_id="feedback1",
                outcome_id="outcome1",
                integrity_id="integrity1",
                execution_id="execution1",
                preparation_id="preparation1",
                decision_id="decision1",
                integrity_decision_id="decision-integrity1",
                proposal_id="proposal1",
                assessment_id="assessment1",
                environment_id="env1",
                expected_model_id="expected",
                observed_model_id="observed",
                feedback_status=EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION,
                confidence=1.0,
                result_fingerprint="fp123",
            )


if __name__ == "__main__":
    unittest.main()
