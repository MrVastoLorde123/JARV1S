from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_decision import (
    LearningWriteAdaptationEvaluationAction,
    LearningWriteAdaptationEvaluationDecisionContext,
    LearningWriteAdaptationEvaluationDecisionService,
)
from src.tools.learning_write_adaptation_evaluation_execution import (
    LearningWriteAdaptationEvaluationExecutionError,
    LearningWriteAdaptationEvaluationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionService,
    LearningWriteAdaptationEvaluationExecutionStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_preparation import (
    LearningWriteAdaptationEvaluationExecutionPreparationContext,
    LearningWriteAdaptationEvaluationExecutionPreparationService,
)
from src.tools.learning_write_adaptation_evaluation_proposal import (
    LearningWriteAdaptationEvaluationProposalContext,
    LearningWriteAdaptationEvaluationProposalService,
)
from src.tools.learning_write_adaptation_evaluation_proposal_admission import (
    LearningWriteAdaptationEvaluationProposalAdmissionContext,
    LearningWriteAdaptationEvaluationProposalAdmissionService,
)
from src.tools.learning_write_adaptation_feedback import LearningWriteAdaptationFeedbackService
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationService,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)


class _RecordingApplier:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.requests = []
        self.result = result
        self.error = error

    def apply(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.result


class LearningWriteAdaptationEvaluationExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = LearningWriteAdaptationOutcome(
            execution_id="adapt-exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            source_candidate_id="source-candidate-1",
            domain="semantic",
            status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
            adaptation_result={"changed": True},
            result_fingerprint="fp-1",
        )
        feedback = LearningWriteAdaptationFeedbackService().from_outcome(outcome)
        evaluation = LearningWriteAdaptationFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationEvaluationDecisionService().decide(
            LearningWriteAdaptationEvaluationDecisionContext(evaluation=evaluation)
        )
        self.assertEqual(decision.action, LearningWriteAdaptationEvaluationAction.ACCEPT)
        proposal = LearningWriteAdaptationEvaluationProposalService().propose(
            LearningWriteAdaptationEvaluationProposalContext(
                decision=decision,
                proposal={"strategy": {"mode": "retain"}},
            )
        )
        admission = LearningWriteAdaptationEvaluationProposalAdmissionService().admit(
            LearningWriteAdaptationEvaluationProposalAdmissionContext(proposal=proposal)
        )
        self.preparation = LearningWriteAdaptationEvaluationExecutionPreparationService().prepare(
            proposal,
            admission,
        )

    def test_completed_execution_returns_result(self) -> None:
        applier = _RecordingApplier(result={"changed": True})
        result = LearningWriteAdaptationEvaluationExecutionService(applier).execute(self.preparation)
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED)
        self.assertEqual(result.execution_result, {"changed": True})
        self.assertEqual(len(applier.requests), 1)

    def test_failure_is_normalized(self) -> None:
        applier = _RecordingApplier(error=RuntimeError("boom"))
        result = LearningWriteAdaptationEvaluationExecutionService(applier).execute(self.preparation)
        self.assertEqual(result.status, LearningWriteAdaptationEvaluationExecutionStatus.FAILED)
        self.assertEqual(result.reason, "boom")

    def test_execution_id_is_deterministic(self) -> None:
        first = LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier(result=1)).execute(self.preparation)
        second = LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier(result=2)).execute(self.preparation)
        self.assertEqual(first.execution_id, second.execution_id)

    def test_execution_id_is_distinct_from_preparation_and_source_execution(self) -> None:
        result = LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier(result=1)).execute(self.preparation)
        self.assertNotEqual(result.execution_id, self.preparation.preparation_id)
        self.assertNotEqual(result.execution_id, self.preparation.source_execution_id)

    def test_exact_lineage_is_preserved(self) -> None:
        applier = _RecordingApplier(result=True)
        result = LearningWriteAdaptationEvaluationExecutionService(applier).execute(self.preparation)
        self.assertEqual(result.preparation_id, self.preparation.preparation_id)
        self.assertEqual(result.admission_id, self.preparation.admission_id)
        self.assertEqual(result.proposal_id, self.preparation.proposal_id)
        self.assertEqual(result.decision_id, self.preparation.decision_id)
        self.assertEqual(result.evaluation_id, self.preparation.evaluation_id)
        self.assertEqual(result.feedback_id, self.preparation.feedback_id)
        self.assertEqual(result.source_feedback_id, self.preparation.source_feedback_id)
        self.assertEqual(result.candidate_id, self.preparation.candidate_id)
        self.assertEqual(result.source_candidate_id, self.preparation.source_candidate_id)
        self.assertEqual(result.source_execution_id, self.preparation.source_execution_id)
        self.assertEqual(result.domain, self.preparation.domain)
        self.assertEqual(result.policy_id, self.preparation.policy_id)

    def test_request_is_bound_to_exact_preparation(self) -> None:
        applier = _RecordingApplier(result=True)
        LearningWriteAdaptationEvaluationExecutionService(applier).execute(self.preparation)
        request = applier.requests[0]
        self.assertEqual(request.preparation_id, self.preparation.preparation_id)
        self.assertEqual(dict(request.payload), dict(self.preparation.payload))

    def test_result_is_immutable(self) -> None:
        result = LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier(result=True)).execute(self.preparation)
        with self.assertRaises(FrozenInstanceError):
            result.domain = "other"  # type: ignore[misc]

    def test_request_is_immutable(self) -> None:
        applier = _RecordingApplier(result=True)
        LearningWriteAdaptationEvaluationExecutionService(applier).execute(self.preparation)
        with self.assertRaises(FrozenInstanceError):
            applier.requests[0].domain = "other"  # type: ignore[misc]

    def test_execution_rejects_authorized_preparation(self) -> None:
        from dataclasses import replace

        invalid = replace(self.preparation, execution_authorized=True)
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionError):
            LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier()).execute(invalid)

    def test_execution_result_requires_failure_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionError):
            LearningWriteAdaptationEvaluationExecutionResult(
                execution_id="exec",
                preparation_id="prep",
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
                status=LearningWriteAdaptationEvaluationExecutionStatus.FAILED,
            )

    def test_request_requires_string_identities(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionError):
            LearningWriteAdaptationEvaluationExecutionRequest(
                execution_id="",
                preparation_id="prep",
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
                payload={},
            )

    def test_to_context_marks_execution_completed_only_after_result(self) -> None:
        result = LearningWriteAdaptationEvaluationExecutionService(_RecordingApplier(result=True)).execute(self.preparation)
        context = result.to_context()
        self.assertTrue(context["execution_completed"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])

    def test_service_rejects_invalid_applier(self) -> None:
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionService(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
