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
    LearningWriteAdaptationExecutionRequest,
    LearningWriteAdaptationExecutionResult,
    LearningWriteAdaptationExecutionStatus,
)
from src.tools.learning_write_adaptation_feedback import (
    LearningWriteAdaptationFeedbackError,
    LearningWriteAdaptationFeedbackEvent,
    LearningWriteAdaptationFeedbackKind,
    LearningWriteAdaptationFeedbackService,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
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


class LearningWriteAdaptationFeedbackTests(unittest.TestCase):
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
        self.outcome_service = LearningWriteAdaptationOutcomeService()
        self.feedback_service = LearningWriteAdaptationFeedbackService()

    def _success_outcome(self) -> LearningWriteAdaptationOutcome:
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
            adaptation_result={"changed": True, "strategy": "prefer_cached_result"},
        )
        return self.outcome_service.interpret(result, self.request)

    def _failure_outcome(self) -> LearningWriteAdaptationOutcome:
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
        return self.outcome_service.interpret(result, self.request)

    def test_successful_outcome_becomes_success_feedback(self) -> None:
        feedback = self.feedback_service.from_outcome(self._success_outcome())
        self.assertEqual(feedback.kind, LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS)
        self.assertEqual(feedback.payload["outcome_status"], "succeeded")
        self.assertEqual(feedback.payload["adaptation_result"]["changed"], True)
        self.assertIsNotNone(feedback.payload["result_fingerprint"])

    def test_failed_outcome_becomes_failure_feedback(self) -> None:
        feedback = self.feedback_service.from_outcome(self._failure_outcome())
        self.assertEqual(feedback.kind, LearningWriteAdaptationFeedbackKind.ADAPTATION_FAILURE)
        self.assertEqual(feedback.payload["outcome_status"], "failed")
        self.assertEqual(feedback.payload["reason"], "applier unavailable")

    def test_exact_lineage_is_preserved(self) -> None:
        outcome = self._success_outcome()
        feedback = self.feedback_service.from_outcome(outcome)
        self.assertEqual(feedback.execution_id, outcome.execution_id)
        self.assertEqual(feedback.admission_id, outcome.admission_id)
        self.assertEqual(feedback.proposal_id, outcome.proposal_id)
        self.assertEqual(feedback.decision_id, outcome.decision_id)
        self.assertEqual(feedback.candidate_id, outcome.candidate_id)
        self.assertEqual(feedback.source_feedback_id, outcome.feedback_id)
        self.assertEqual(feedback.source_candidate_id, outcome.source_candidate_id)
        self.assertEqual(feedback.domain, outcome.domain)

    def test_feedback_id_is_deterministic(self) -> None:
        outcome = self._success_outcome()
        first = self.feedback_service.from_outcome(outcome)
        second = self.feedback_service.from_outcome(outcome)
        self.assertEqual(first.feedback_id, second.feedback_id)

    def test_payload_is_recursively_immutable(self) -> None:
        mutable_result = {"nested": {"items": [1, 2]}}
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
            adaptation_result=mutable_result,
        )
        outcome = self.outcome_service.interpret(result, self.request)
        feedback = self.feedback_service.from_outcome(outcome)
        mutable_result["nested"]["items"].append(3)
        with self.assertRaises(TypeError):
            feedback.payload["adaptation_result"]["nested"]["items"][0] = 99  # type: ignore[index]
        self.assertEqual(feedback.payload["adaptation_result"]["nested"]["items"], (1, 2))

    def test_provenance_is_recursively_immutable(self) -> None:
        feedback = self.feedback_service.from_outcome(self._success_outcome())
        with self.assertRaises(TypeError):
            feedback.provenance["execution_id"] = "other"  # type: ignore[index]

    def test_event_is_immutable(self) -> None:
        feedback = self.feedback_service.from_outcome(self._success_outcome())
        with self.assertRaises(FrozenInstanceError):
            feedback.kind = LearningWriteAdaptationFeedbackKind.ADAPTATION_FAILURE  # type: ignore[misc]

    def test_success_context_is_non_authorizing_and_non_writing(self) -> None:
        context = self.feedback_service.from_outcome(self._success_outcome()).to_context()
        self.assertTrue(context["adaptation_applied"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_failure_context_does_not_claim_adaptation_applied(self) -> None:
        context = self.feedback_service.from_outcome(self._failure_outcome()).to_context()
        self.assertFalse(context["adaptation_applied"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])

    def test_success_feedback_requires_non_empty_reason_and_provenance(self) -> None:
        with self.assertRaises(LearningWriteAdaptationFeedbackError):
            LearningWriteAdaptationFeedbackEvent(
                feedback_id="feedback-1",
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                source_feedback_id="source-feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                kind=LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS,
                payload={},
                provenance={"source": ""},
                reason="ok",
            )

    def test_invalid_outcome_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.feedback_service.from_outcome({"bad": True})  # type: ignore[arg-type]

    def test_invalid_kind_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationFeedbackError):
            LearningWriteAdaptationFeedbackEvent(
                feedback_id="feedback-1",
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                source_feedback_id="source-feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                kind="adaptation_success",  # type: ignore[arg-type]
                payload={},
                provenance={"source": "test"},
                reason="ok",
            )

    def test_source_feedback_identity_is_present_in_context_and_provenance(self) -> None:
        outcome = self._success_outcome()
        feedback = self.feedback_service.from_outcome(outcome)
        context = feedback.to_context()
        self.assertEqual(context["learning_write_feedback_id"], outcome.feedback_id)
        self.assertEqual(feedback.provenance["feedback_id"], outcome.feedback_id)


if __name__ == "__main__":
    unittest.main()
