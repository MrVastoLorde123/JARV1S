from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_admission import (
    LearningWriteAdaptationAdmissionContext,
    LearningWriteAdaptationAdmissionService,
)
from src.tools.learning_write_adaptation_decision import (
    LearningWriteAdaptationDecisionContext,
    LearningWriteAdaptationDecisionService,
)
from src.tools.learning_write_adaptation_execution import (
    LearningWriteAdaptationExecutionResult,
    LearningWriteAdaptationExecutionRequest,
    LearningWriteAdaptationExecutionStatus,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeError,
    LearningWriteAdaptationOutcomeService,
    LearningWriteAdaptationOutcomeStatus,
)
from src.tools.learning_write_adaptation_proposal import (
    LearningWriteAdaptationProposalContext,
    LearningWriteAdaptationProposalService,
)
from src.tools.learning_write_feedback import LearningWriteFeedbackService
from src.tools.learning_write_feedback_evaluation import LearningWriteFeedbackEvaluationService
from src.tools.learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus


class LearningWriteAdaptationOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        write_outcome = LearningWriteOutcome(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            status=LearningWriteOutcomeStatus.SUCCEEDED,
            write_result={"memory_id": 42},
            result_fingerprint="fp-1",
        )
        feedback = LearningWriteFeedbackService().from_outcome(write_outcome)
        candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationDecisionService().decide(
            LearningWriteAdaptationDecisionContext(candidate=candidate)
        )
        proposal = LearningWriteAdaptationProposalService().propose(
            LearningWriteAdaptationProposalContext(
                decision=decision,
                candidate=candidate,
                adaptation={"strategy": "prefer_cached_result"},
            )
        )
        self.assertIsNotNone(proposal)
        self.proposal = proposal
        self.admission = LearningWriteAdaptationAdmissionService().admit(
            LearningWriteAdaptationAdmissionContext(proposal)
        )
        self.request = LearningWriteAdaptationExecutionRequest(
            execution_id="adapt-exec-1",
            admission_id=self.admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            feedback_id=proposal.feedback_id,
            source_candidate_id=proposal.proposal_source_candidate_id,
            domain=proposal.domain,
            adaptation=proposal.adaptation,
        )
        self.service = LearningWriteAdaptationOutcomeService()

    def test_completed_result_becomes_successful_outcome(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"changed": True},
        )
        outcome = self.service.interpret(result, self.request)
        self.assertEqual(outcome.status, LearningWriteAdaptationOutcomeStatus.SUCCEEDED)
        self.assertEqual(outcome.adaptation_result, {"changed": True})
        self.assertIsNotNone(outcome.result_fingerprint)

    def test_failed_result_becomes_failed_outcome(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.FAILED,
            reason="applier unavailable",
        )
        outcome = self.service.interpret(result, self.request)
        self.assertEqual(outcome.status, LearningWriteAdaptationOutcomeStatus.FAILED)
        self.assertEqual(outcome.reason, "applier unavailable")
        self.assertIsNone(outcome.result_fingerprint)

    def test_exact_lineage_is_preserved(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        outcome = self.service.interpret(result, self.request)
        self.assertEqual(outcome.execution_id, self.request.execution_id)
        self.assertEqual(outcome.admission_id, self.request.admission_id)
        self.assertEqual(outcome.proposal_id, self.request.proposal_id)
        self.assertEqual(outcome.decision_id, self.request.decision_id)
        self.assertEqual(outcome.candidate_id, self.request.candidate_id)
        self.assertEqual(outcome.feedback_id, self.request.feedback_id)
        self.assertEqual(outcome.source_candidate_id, self.request.source_candidate_id)
        self.assertEqual(outcome.domain, self.request.domain)

    def test_result_fingerprint_is_deterministic(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"a": 1, "b": 2},
        )
        first = self.service.interpret(result, self.request)
        second = self.service.interpret(result, self.request)
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_identity_mismatch_is_rejected(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id="wrong-execution",
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        with self.assertRaises(LearningWriteAdaptationOutcomeError):
            self.service.interpret(result, self.request)

    def test_outcome_is_immutable(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        outcome = self.service.interpret(result, self.request)
        with self.assertRaises(FrozenInstanceError):
            outcome.status = LearningWriteAdaptationOutcomeStatus.FAILED  # type: ignore[misc]

    def test_success_requires_fingerprint(self) -> None:
        with self.assertRaises(LearningWriteAdaptationOutcomeError):
            LearningWriteAdaptationOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
            )

    def test_failed_requires_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationOutcomeError):
            LearningWriteAdaptationOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                status=LearningWriteAdaptationOutcomeStatus.FAILED,
            )

    def test_success_cannot_contain_failure_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationOutcomeError):
            LearningWriteAdaptationOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
                result_fingerprint="fp",
                reason="bad",
            )

    def test_failed_cannot_contain_fingerprint(self) -> None:
        with self.assertRaises(LearningWriteAdaptationOutcomeError):
            LearningWriteAdaptationOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                status=LearningWriteAdaptationOutcomeStatus.FAILED,
                result_fingerprint="fp",
                reason="failed",
            )

    def test_outcome_is_non_authorizing_and_non_writing(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        outcome = self.service.interpret(result, self.request)
        context = outcome.to_context()
        self.assertTrue(context["adaptation_applied"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_result_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret({"bad": True}, self.request)  # type: ignore[arg-type]

    def test_invalid_request_type_is_rejected(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id=self.request.execution_id,
            admission_id=self.request.admission_id,
            proposal_id=self.request.proposal_id,
            decision_id=self.request.decision_id,
            candidate_id=self.request.candidate_id,
            feedback_id=self.request.feedback_id,
            source_candidate_id=self.request.source_candidate_id,
            domain=self.request.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        with self.assertRaises(TypeError):
            self.service.interpret(result, {"bad": True})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
