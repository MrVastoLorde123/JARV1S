from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_execution import (
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionApplier,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService,
    LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
)


class RecordingApplier:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.requests: list[LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest] = []

    def apply(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.result


def build_preparation(**overrides):
    values = dict(
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
        execution_id="prior-execution-1",
        source_execution_id="source-execution-0",
        source_admission_id="source-admission-0",
        proposal_source_id="proposal-source-1",
        domain="semantic",
        source_policy_id="source-policy-1",
        policy_id="admission-policy-1",
        payload={"strategy": {"mode": "retain"}},
        evidence={"reason": "accepted"},
        provenance={"source": "m22.40", "admission_id": "admission-1"},
    )
    values.update(overrides)
    return LearningWriteAdaptationEvaluationExecutionFeedbackPreparation(**values)


class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionTests(unittest.TestCase):
    def test_admitted_preparation_executes_through_applier(self) -> None:
        applier = RecordingApplier(result={"changed": True})
        result = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(applier).execute(
            build_preparation()
        )
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED)
        self.assertEqual(result.execution_result, {"changed": True})
        self.assertEqual(len(applier.requests), 1)

    def test_execution_request_preserves_full_lineage(self) -> None:
        applier = RecordingApplier(result=True)
        preparation = build_preparation()
        result = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(applier).execute(preparation)
        request = applier.requests[0]
        for field in (
            "preparation_id", "admission_id", "proposal_id", "decision_id", "evaluation_id",
            "decision_source_evaluation_id", "feedback_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "source_execution_id", "source_admission_id", "proposal_source_id",
            "domain", "source_policy_id", "policy_id",
        ):
            expected = getattr(preparation, field)
            actual_field = "execution_source_id" if field == "execution_id" else field
            if field == "execution_id":
                self.assertEqual(request.execution_source_id, preparation.execution_id)
            else:
                self.assertEqual(getattr(request, actual_field), expected)
        self.assertEqual(result.execution_source_id, preparation.execution_id)
        self.assertEqual(result.source_execution_id, preparation.source_execution_id)
        self.assertNotEqual(result.execution_id, preparation.execution_id)

    def test_execution_id_is_deterministic(self) -> None:
        first = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier(result=1)).execute(
            build_preparation()
        )
        second = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier(result=2)).execute(
            build_preparation()
        )
        self.assertEqual(first.execution_id, second.execution_id)

    def test_preparation_payload_evidence_and_provenance_are_frozen_in_request(self) -> None:
        applier = RecordingApplier(result=True)
        LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(applier).execute(build_preparation())
        request = applier.requests[0]
        with self.assertRaises(TypeError):
            request.payload["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            request.evidence["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            request.provenance["new"] = "blocked"  # type: ignore[index]

    def test_applier_exception_becomes_failed_result(self) -> None:
        applier = RecordingApplier(error=RuntimeError("boom"))
        result = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(applier).execute(
            build_preparation()
        )
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.FAILED)
        self.assertEqual(result.reason, "boom")
        self.assertIsNone(result.execution_result)

    def test_completed_result_cannot_have_failure_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult(
                execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
                proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
                decision_source_evaluation_id="historical-evaluation-1", feedback_id="feedback-1",
                source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="prior-execution-1", source_execution_id="source-execution-0",
                source_admission_id="source-admission-0", proposal_source_id="proposal-source-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED,
                reason="not allowed",
            )

    def test_failed_result_requires_non_empty_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult(
                execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
                proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
                decision_source_evaluation_id="historical-evaluation-1", feedback_id="feedback-1",
                source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
                execution_source_id="prior-execution-1", source_execution_id="source-execution-0",
                source_admission_id="source-admission-0", proposal_source_id="proposal-source-1",
                domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
                status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.FAILED,
                reason="",
            )

    def test_invalid_preparation_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier()).execute({})  # type: ignore[arg-type]

    def test_authority_wall_is_preserved(self) -> None:
        result = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier(result=True)).execute(
            build_preparation()
        )
        context = result.to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])

    def test_authorized_preparation_is_rejected(self) -> None:
        preparation = object.__new__(LearningWriteAdaptationEvaluationExecutionFeedbackPreparation)
        for name, value in build_preparation().__dict__.items():
            object.__setattr__(preparation, name, value)
        object.__setattr__(preparation, "execution_authorized", True)
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier()).execute(preparation)

    def test_started_preparation_is_rejected(self) -> None:
        preparation = object.__new__(LearningWriteAdaptationEvaluationExecutionFeedbackPreparation)
        for name, value in build_preparation().__dict__.items():
            object.__setattr__(preparation, name, value)
        object.__setattr__(preparation, "execution_started", True)
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError):
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier()).execute(preparation)

    def test_retry_revocation_or_mutation_flags_are_rejected(self) -> None:
        for field in ("retry_requested", "revocation_requested", "memory_mutation_allowed", "authority_granted"):
            preparation = object.__new__(LearningWriteAdaptationEvaluationExecutionFeedbackPreparation)
            for name, value in build_preparation().__dict__.items():
                object.__setattr__(preparation, name, value)
            object.__setattr__(preparation, field, True)
            with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError):
                LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(RecordingApplier()).execute(preparation)

    def test_request_is_immutable(self) -> None:
        request = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest(
            execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
            proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
            decision_source_evaluation_id="historical-evaluation-1", feedback_id="feedback-1",
            source_feedback_id="source-feedback-1", candidate_id="candidate-1", source_candidate_id="source-candidate-1",
            execution_source_id="prior-execution-1", source_execution_id="source-execution-0",
            source_admission_id="source-admission-0", proposal_source_id="proposal-source-1",
            domain="semantic", source_policy_id="source-policy-1", policy_id="policy-1",
            payload={"a": 1}, evidence={"b": 2}, provenance={"source": "test"},
        )
        with self.assertRaises(FrozenInstanceError):
            request.domain = "other"  # type: ignore[misc]

    def test_applier_interface_is_replaceable(self) -> None:
        class MinimalApplier:
            def apply(self, request):
                return request.payload["strategy"]["mode"]

        result = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService(MinimalApplier()).execute(
            build_preparation()
        )
        self.assertEqual(result.execution_result, "retain")


if __name__ == "__main__":
    unittest.main()
