from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from src.tools.learning_write_adaptation_evaluation_execution import (
    LearningWriteAdaptationEvaluationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_result import (
    LearningWriteAdaptationEvaluationExecutionOutcome,
    LearningWriteAdaptationEvaluationExecutionOutcomeStatus,
    LearningWriteAdaptationEvaluationExecutionResultIntegrityError,
    LearningWriteAdaptationEvaluationExecutionResultIntegrityService,
)


class LearningWriteAdaptationEvaluationExecutionResultIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = LearningWriteAdaptationEvaluationExecutionRequest(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-1",
            payload={"strategy": {"mode": "retain"}},
        )
        self.result = LearningWriteAdaptationEvaluationExecutionResult(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED,
            execution_result={"changed": True, "score": 0.91},
        )
        self.service = LearningWriteAdaptationEvaluationExecutionResultIntegrityService()

    def test_success_is_normalized_and_fingerprinted(self) -> None:
        outcome = self.service.interpret(self.result, self.request)
        self.assertEqual(outcome.status, LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED)
        self.assertEqual(outcome.execution_result, {"changed": True, "score": 0.91})
        self.assertIsNotNone(outcome.result_fingerprint)
        self.assertIsNone(outcome.reason)

    def test_fingerprint_is_deterministic(self) -> None:
        first = self.service.interpret(self.result, self.request)
        second = self.service.interpret(self.result, self.request)
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_fingerprint_is_order_insensitive_for_mappings(self) -> None:
        first_result = self.result
        second_result = LearningWriteAdaptationEvaluationExecutionResult(
            **{**first_result.__dict__, "execution_result": {"score": 0.91, "changed": True}}
        )
        first = self.service.interpret(first_result, self.request)
        second = self.service.interpret(second_result, self.request)
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_failure_requires_reason_and_has_no_fingerprint(self) -> None:
        failed = LearningWriteAdaptationEvaluationExecutionResult(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            source_execution_id="source-execution-1",
            domain="semantic",
            policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionStatus.FAILED,
            reason="applier failed",
        )
        outcome = self.service.interpret(failed, self.request)
        self.assertEqual(outcome.status, LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED)
        self.assertEqual(outcome.reason, "applier failed")
        self.assertIsNone(outcome.result_fingerprint)

    def test_exact_lineage_is_preserved(self) -> None:
        outcome = self.service.interpret(self.result, self.request)
        for field_name in (
            "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "feedback_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "source_execution_id", "domain", "policy_id",
        ):
            self.assertEqual(getattr(outcome, field_name), getattr(self.request, field_name))

    def test_identity_mismatch_is_rejected(self) -> None:
        mismatched = LearningWriteAdaptationEvaluationExecutionResult(
            **{**self.result.__dict__, "policy_id": "other-policy"}
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionResultIntegrityError):
            self.service.interpret(mismatched, self.request)

    def test_preparation_mismatch_is_rejected(self) -> None:
        mismatched = LearningWriteAdaptationEvaluationExecutionResult(
            **{**self.result.__dict__, "preparation_id": "other-preparation"}
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionResultIntegrityError):
            self.service.interpret(mismatched, self.request)

    def test_source_feedback_mismatch_is_rejected(self) -> None:
        mismatched = LearningWriteAdaptationEvaluationExecutionResult(
            **{**self.result.__dict__, "source_feedback_id": "other-source-feedback"}
        )
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionResultIntegrityError):
            self.service.interpret(mismatched, self.request)

    def test_result_and_request_types_are_required(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret(SimpleNamespace(), self.request)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.service.interpret(self.result, SimpleNamespace())  # type: ignore[arg-type]

    def test_outcome_is_immutable(self) -> None:
        outcome = self.service.interpret(self.result, self.request)
        with self.assertRaises(FrozenInstanceError):
            outcome.domain = "other"  # type: ignore[misc]

    def test_success_cannot_carry_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionOutcome(
                execution_id="execution",
                preparation_id="preparation",
                admission_id="admission",
                proposal_id="proposal",
                decision_id="decision",
                evaluation_id="evaluation",
                feedback_id="feedback",
                source_feedback_id="source-feedback",
                candidate_id="candidate",
                source_candidate_id="source-candidate",
                source_execution_id="source-execution",
                domain="semantic",
                policy_id="policy",
                status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED,
                result_fingerprint="fingerprint",
                reason="invalid",
            )

    def test_failed_outcome_cannot_have_fingerprint(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionResultIntegrityError):
            LearningWriteAdaptationEvaluationExecutionOutcome(
                execution_id="execution",
                preparation_id="preparation",
                admission_id="admission",
                proposal_id="proposal",
                decision_id="decision",
                evaluation_id="evaluation",
                feedback_id="feedback",
                source_feedback_id="source-feedback",
                candidate_id="candidate",
                source_candidate_id="source-candidate",
                source_execution_id="source-execution",
                domain="semantic",
                policy_id="policy",
                status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED,
                result_fingerprint="fingerprint",
                reason="failed",
            )

    def test_to_context_preserves_authority_wall(self) -> None:
        outcome = self.service.interpret(self.result, self.request)
        context = outcome.to_context()
        self.assertTrue(context["execution_result_integrity_verified"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["adaptation_truth_proven"])

    def test_outcome_identity_remains_execution_id(self) -> None:
        outcome = self.service.interpret(self.result, self.request)
        self.assertEqual(outcome.to_context()["learning_write_adaptation_evaluation_execution_outcome_id"], "execution-1")


if __name__ == "__main__":
    unittest.main()
