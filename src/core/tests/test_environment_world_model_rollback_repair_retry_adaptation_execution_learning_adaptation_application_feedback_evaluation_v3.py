import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)


class M23_79AdaptationApplicationFeedbackEvaluationV3Tests(unittest.TestCase):
    def _make_feedback(self, status):
        failure = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL
        rejection = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL
        outcome = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED,
        }[status]
        application_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED if (failure or rejection) else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED
        decision_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED if rejection else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3(
            feedback_id="feedback-79",
            classification_id="classification-79",
            integrity_id="integrity-76",
            application_id="application-79",
            decision_id="decision-79",
            proposal_id="proposal-79",
            source_proposal_id="source-proposal-79",
            eligibility_id="eligibility-79",
            source_integrity_id="source-integrity-79",
            signal_id="signal-79",
            evaluation_id="evaluation-source-79",
            feedback_source_id="classification-79",
            execution_id="execution-79",
            handoff_id="handoff-79",
            authorization_id="authorization-79",
            validation_id="validation-79",
            source_signal_id="source-signal-79",
            outcome_id="outcome-79",
            preparation_id="preparation-79",
            assessment_id="assessment-79",
            environment_id="environment-79",
            expected_model_id="expected-79",
            observed_model_id="observed-79",
            confidence=0.91,
            signal_fingerprint="a" * 64,
            upstream_proposal_fingerprint="b" * 64,
            handoff_fingerprint="0" * 64 if rejection else "c" * 64,
            result_fingerprint="0" * 64 if (failure or rejection) else "d" * 64,
            application_fingerprint="e" * 64,
            authority_principal_id=None if rejection else "user:test",
            executor_id=None if rejection else "executor:test",
            proposal_kind="ADAPTATION_CANDIDATE",
            proposal_status="PROPOSED",
            decision_status=decision_status,
            application_status=application_status,
            integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID,
            outcome_status=outcome,
            feedback_status=status,
            failure_reason="applier failed" if failure else None,
            reasons={"source": "test"},
            lineage={"nested": {"id": "79"}},
        )

    def test_success_becomes_success_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL),
            evaluation_id="evaluation-79",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION)

    def test_failure_becomes_failure_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL),
            evaluation_id="evaluation-79",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_rejection_becomes_rejection_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL),
            evaluation_id="evaluation-79",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION)
        self.assertIsNone(result.authority_principal_id)
        self.assertIsNone(result.executor_id)
        self.assertIsNone(result.failure_reason)

    def test_blank_evaluation_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
                self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL), evaluation_id=" "
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(object(), evaluation_id="evaluation-79")

    def test_confidence_is_bounded(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL)
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service()
        with self.assertRaises(ValueError):
            service.evaluate(source, evaluation_id="evaluation-79", confidence=1.1)
        with self.assertRaises(ValueError):
            service.evaluate(source, evaluation_id="evaluation-79", confidence=-0.1)

    def test_evaluation_status_mismatch_is_rejected(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3(
                evaluation_id="evaluation-79", feedback_id=source.feedback_id, classification_id=source.classification_id,
                integrity_id=source.integrity_id, application_id=source.application_id, decision_id=source.decision_id,
                proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id, eligibility_id=source.eligibility_id,
                source_integrity_id=source.source_integrity_id, signal_id=source.signal_id, source_evaluation_id=source.evaluation_id,
                feedback_source_id=source.feedback_source_id, execution_id=source.execution_id, handoff_id=source.handoff_id,
                authorization_id=source.authorization_id, validation_id=source.validation_id, source_signal_id=source.source_signal_id,
                outcome_id=source.outcome_id, preparation_id=source.preparation_id, assessment_id=source.assessment_id,
                environment_id=source.environment_id, expected_model_id=source.expected_model_id, observed_model_id=source.observed_model_id,
                confidence=1.0, signal_fingerprint=source.signal_fingerprint, upstream_proposal_fingerprint=source.upstream_proposal_fingerprint,
                handoff_fingerprint=source.handoff_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, authority_principal_id=source.authority_principal_id,
                executor_id=source.executor_id, proposal_kind=source.proposal_kind, proposal_status=source.proposal_status,
                decision_status=source.decision_status, application_status=source.application_status, integrity_status=source.integrity_status,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION,
                failure_reason=source.failure_reason,
            )

    def test_full_provenance_and_fingerprints_are_preserved(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(source, evaluation_id="evaluation-79", confidence=0.73)
        for field in (
            "feedback_id", "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id",
            "source_proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "source_evaluation_id",
            "feedback_source_id", "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id",
            "outcome_id", "preparation_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "application_fingerprint",
        ):
            self.assertEqual(getattr(result, field), getattr(source, "evaluation_id" if field == "source_evaluation_id" else field))
        self.assertEqual(result.confidence, 0.73)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL),
            evaluation_id="evaluation-79", reasons={"outer": "reason"}, lineage={"nested": {"x": [1, 2]}}
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["nested"]["new"] = "blocked"

    def test_source_is_unchanged(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(source, evaluation_id="evaluation-79")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL)

    def test_evaluation_is_advisory_only(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL), evaluation_id="evaluation-79"
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_rejection_evaluation_cannot_carry_authority_or_executor(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3(
                evaluation_id="evaluation-79", feedback_id=source.feedback_id, classification_id=source.classification_id,
                integrity_id=source.integrity_id, application_id=source.application_id, decision_id=source.decision_id,
                proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id, eligibility_id=source.eligibility_id,
                source_integrity_id=source.source_integrity_id, signal_id=source.signal_id, source_evaluation_id=source.evaluation_id,
                feedback_source_id=source.feedback_source_id, execution_id=source.execution_id, handoff_id=source.handoff_id,
                authorization_id=source.authorization_id, validation_id=source.validation_id, source_signal_id=source.source_signal_id,
                outcome_id=source.outcome_id, preparation_id=source.preparation_id, assessment_id=source.assessment_id,
                environment_id=source.environment_id, expected_model_id=source.expected_model_id, observed_model_id=source.observed_model_id,
                confidence=1.0, signal_fingerprint=source.signal_fingerprint, upstream_proposal_fingerprint=source.upstream_proposal_fingerprint,
                handoff_fingerprint=source.handoff_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, authority_principal_id="user:should-not-pass",
                executor_id="executor:should-not-pass", proposal_kind=source.proposal_kind, proposal_status=source.proposal_status,
                decision_status=source.decision_status, application_status=source.application_status, integrity_status=source.integrity_status,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION,
                failure_reason=source.failure_reason,
            )


if __name__ == "__main__":
    unittest.main()
