from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_execution import (
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity import (
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityService,
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            decision_source_evaluation_id="historical-evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1",
            source_execution_id="source-execution-1",
            source_admission_id="source-admission-1",
            proposal_source_id="source-proposal-1",
            domain="semantic",
            source_policy_id="source-policy-1",
            policy_id="policy-1",
            payload={"strategy": {"mode": "retain"}},
            evidence={"confidence": 0.8},
            provenance={"source": "test"},
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityService()

    def _result(self, **overrides):
        data = dict(
            execution_id=self.request.execution_id,
            preparation_id=self.request.preparation_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            evaluation_id=self.request.evaluation_id,
            decision_source_evaluation_id=self.request.decision_source_evaluation_id,
            feedback_id=self.request.feedback_id,
            source_feedback_id=self.request.source_feedback_id,
            candidate_id=self.request.candidate_id,
            source_candidate_id=self.request.source_candidate_id,
            execution_source_id=self.request.execution_source_id,
            source_execution_id=self.request.source_execution_id,
            source_admission_id=self.request.source_admission_id,
            proposal_source_id=self.request.proposal_source_id,
            domain=self.request.domain,
            source_policy_id=self.request.source_policy_id,
            policy_id=self.request.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED,
            execution_result={"changed": True},
        )
        data.update(overrides)
        return LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult(**data)

    def test_successful_result_becomes_succeeded_integrity_evidence(self) -> None:
        outcome = self.service.interpret(self._result(), self.request)
        self.assertIsInstance(outcome, LearningWriteAdaptationEvaluationExecutionFeedbackOutcome)
        self.assertEqual(outcome.status, LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED)
        self.assertTrue(outcome.result_fingerprint)
        self.assertIsNone(outcome.reason)

    def test_failed_result_becomes_failed_integrity_evidence(self) -> None:
        result = self._result(
            status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.FAILED,
            execution_result=None,
            reason="applier failed",
        )
        outcome = self.service.interpret(result, self.request)
        self.assertEqual(outcome.status, LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.FAILED)
        self.assertEqual(outcome.reason, "applier failed")
        self.assertIsNone(outcome.result_fingerprint)

    def test_full_lineage_is_preserved(self) -> None:
        outcome = self.service.interpret(self._result(), self.request)
        for field in (
            "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "decision_source_evaluation_id", "feedback_id", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "source_admission_id", "proposal_source_id", "domain", "source_policy_id", "policy_id",
        ):
            self.assertEqual(getattr(outcome, field), getattr(self.request, field))

    def test_mismatched_execution_identity_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError):
            self.service.interpret(self._result(execution_id="wrong"), self.request)

    def test_mismatched_lineage_identity_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError):
            self.service.interpret(self._result(source_admission_id="wrong"), self.request)

    def test_invalid_result_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret({"bad": True}, self.request)  # type: ignore[arg-type]

    def test_invalid_request_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret(self._result(), {"bad": True})  # type: ignore[arg-type]

    def test_success_result_gets_deterministic_fingerprint(self) -> None:
        first = self.service.interpret(self._result(), self.request)
        second = self.service.interpret(self._result(), self.request)
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_result_payload_is_recursively_immutable(self) -> None:
        outcome = self.service.interpret(self._result(execution_result={"nested": {"value": 1}}), self.request)
        with self.assertRaises(TypeError):
            outcome.execution_result["nested"]["value"] = 2  # type: ignore[index]

    def test_outcome_is_immutable(self) -> None:
        outcome = self.service.interpret(self._result(), self.request)
        with self.assertRaises(FrozenInstanceError):
            outcome.domain = "other"  # type: ignore[misc]

    def test_success_cannot_have_failure_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
                execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
                proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
                decision_source_evaluation_id="historical-evaluation-1", feedback_id="feedback-1",
                source_feedback_id="source-feedback-1", candidate_id="candidate-1",
                source_candidate_id="source-candidate-1", execution_source_id="source-execution-1",
                source_admission_id="source-admission-1", proposal_source_id="source-proposal-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED,
                result_fingerprint="fp", reason="bad",
            )

    def test_failed_outcome_has_no_fingerprint(self) -> None:
        result = self._result(
            status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.FAILED,
            execution_result=None,
            reason="failed",
        )
        outcome = self.service.interpret(result, self.request)
        self.assertIsNone(outcome.result_fingerprint)
        self.assertEqual(outcome.reason, "failed")

    def test_to_context_preserves_integrity_wall(self) -> None:
        outcome = self.service.interpret(self._result(), self.request)
        context = outcome.to_context()
        self.assertTrue(context["execution_result_integrity_verified"])
        self.assertFalse(context["adaptation_truth_proven"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])


if __name__ == "__main__":
    unittest.main()
