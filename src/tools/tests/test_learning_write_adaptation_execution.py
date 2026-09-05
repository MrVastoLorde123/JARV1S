from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_admission import (
    LearningWriteAdaptationAdmissionContext,
    LearningWriteAdaptationAdmissionService,
)
from src.tools.learning_write_adaptation_execution import (
    LearningWriteAdaptationExecutionError,
    LearningWriteAdaptationExecutionRequest,
    LearningWriteAdaptationExecutionResult,
    LearningWriteAdaptationExecutionService,
    LearningWriteAdaptationExecutionStatus,
)
from src.tools.learning_write_adaptation_proposal import (
    LearningWriteAdaptationProposalContext,
    LearningWriteAdaptationProposalService,
)
from src.tools.learning_write_adaptation_decision import (
    LearningWriteAdaptationDecisionContext,
    LearningWriteAdaptationDecisionService,
)
from src.tools.learning_write_feedback import LearningWriteFeedbackService
from src.tools.learning_write_feedback_evaluation import LearningWriteFeedbackEvaluationService
from src.tools.learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus


class LearningWriteAdaptationExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = LearningWriteOutcome(
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
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
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

    class Applier:
        def __init__(self, result=None, error: Exception | None = None) -> None:
            self.result = result
            self.error = error
            self.requests = []

        def apply(self, request: LearningWriteAdaptationExecutionRequest):
            self.requests.append(request)
            if self.error:
                raise self.error
            return self.result

    def test_admitted_proposal_executes(self) -> None:
        applier = self.Applier(result={"changed": True})
        result = LearningWriteAdaptationExecutionService(applier).execute(
            self.admission, self.proposal
        )
        self.assertEqual(result.status, LearningWriteAdaptationExecutionStatus.COMPLETED)
        self.assertEqual(result.adaptation_result, {"changed": True})
        self.assertEqual(len(applier.requests), 1)

    def test_non_admitted_proposal_is_blocked(self) -> None:
        rejected = self.admission.__class__(
            **{**self.admission.__dict__, "status": "rejected"}
        )
        # Build an explicit valid rejected admission through its enum value.
        from src.tools.learning_write_adaptation_admission import LearningWriteAdaptationAdmissionStatus
        rejected = self.admission.__class__(
            **{**self.admission.__dict__, "status": LearningWriteAdaptationAdmissionStatus.REJECTED}
        )
        with self.assertRaises(LearningWriteAdaptationExecutionError):
            LearningWriteAdaptationExecutionService(self.Applier()).execute(
                rejected, self.proposal
            )

    def test_exact_lineage_is_preserved(self) -> None:
        result = LearningWriteAdaptationExecutionService(self.Applier()).execute(
            self.admission, self.proposal
        )
        self.assertEqual(result.admission_id, self.admission.admission_id)
        self.assertEqual(result.proposal_id, self.proposal.proposal_id)
        self.assertEqual(result.decision_id, self.proposal.decision_id)
        self.assertEqual(result.candidate_id, self.proposal.candidate_id)
        self.assertEqual(result.feedback_id, self.proposal.feedback_id)
        self.assertEqual(result.source_candidate_id, self.proposal.proposal_source_candidate_id)
        self.assertEqual(result.domain, self.proposal.domain)

    def test_execution_id_is_deterministic(self) -> None:
        service = LearningWriteAdaptationExecutionService(self.Applier(result={"ok": True}))
        first = service.execute(self.admission, self.proposal)
        second = service.execute(self.admission, self.proposal)
        self.assertEqual(first.execution_id, second.execution_id)

    def test_applier_failure_becomes_failed_result(self) -> None:
        result = LearningWriteAdaptationExecutionService(
            self.Applier(error=RuntimeError("applier unavailable"))
        ).execute(self.admission, self.proposal)
        self.assertEqual(result.status, LearningWriteAdaptationExecutionStatus.FAILED)
        self.assertEqual(result.reason, "applier unavailable")

    def test_result_is_immutable(self) -> None:
        result = LearningWriteAdaptationExecutionResult(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            source_candidate_id="source-1",
            domain="semantic",
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result={"ok": True},
        )
        with self.assertRaises(FrozenInstanceError):
            result.status = LearningWriteAdaptationExecutionStatus.FAILED  # type: ignore[misc]

    def test_execution_request_preserves_input_snapshot(self) -> None:
        request = LearningWriteAdaptationExecutionRequest(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            source_candidate_id="source-1",
            domain="semantic",
            adaptation={"nested": {"value": 1}},
        )
        self.assertEqual(request.adaptation["nested"]["value"], 1)

    def test_execution_is_non_authorizing_and_non_writing(self) -> None:
        result = LearningWriteAdaptationExecutionService(self.Applier(result={"ok": True})).execute(
            self.admission, self.proposal
        )
        context = result.to_context()
        self.assertTrue(context["adaptation_applied"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_identity_mismatch_is_rejected(self) -> None:
        from src.tools.learning_write_adaptation_admission import LearningWriteAdaptationAdmission
        bad = LearningWriteAdaptationAdmission(
            **{**self.admission.__dict__, "proposal_id": "wrong-proposal"}
        )
        with self.assertRaises(LearningWriteAdaptationExecutionError):
            LearningWriteAdaptationExecutionService(self.Applier()).execute(
                bad, self.proposal
            )

    def test_invalid_applier_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            LearningWriteAdaptationExecutionService(object())  # type: ignore[arg-type]

    def test_result_status_contract_is_enforced(self) -> None:
        with self.assertRaises(LearningWriteAdaptationExecutionError):
            LearningWriteAdaptationExecutionResult(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                source_candidate_id="source-1",
                domain="semantic",
                status=LearningWriteAdaptationExecutionStatus.FAILED,
            )


if __name__ == "__main__":
    unittest.main()
