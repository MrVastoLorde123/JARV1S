from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_admission import (
    DeterministicLearningWriteAdmissionProvider,
    LearningWriteAdmission,
    LearningWriteAdmissionContext,
    LearningWriteAdmissionStatus,
    LearningWriteDomain,
)
from src.tools.learning_write_execution import (
    LearningWriteExecutionError,
    LearningWriteExecutionService,
    LearningWriteExecutionStatus,
)
from src.tools.learning_write_proposal import (
    LearningWriteProposal,
)


class RecordingWriter:
    def __init__(self, result=None, error=None) -> None:
        self.result = result
        self.error = error
        self.requests = []

    def write(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.result


class LearningWriteExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = self._proposal()
        self.admission = DeterministicLearningWriteAdmissionProvider().admit(
            LearningWriteAdmissionContext(self.proposal)
        )

    @staticmethod
    def _proposal(proposal_id: str = "proposal-1") -> LearningWriteProposal:
        from src.tools.feedback_evaluation import LearningCandidate, LearningSignalKind
        candidate = LearningCandidate(
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            execution_id="exec-1",
            handoff_id="handoff-1",
            tool_name="echo",
            signal=LearningSignalKind.SUCCESS_SIGNAL,
            confidence=0.8,
            evidence={"observed": True},
            provenance={"source": "execution_feedback", "feedback_id": "feedback-1"},
            reason="observed success",
        )
        from src.tools.learning_decision import LearningAction, LearningDecision
        decision = LearningDecision(
            decision_id="decision-1",
            candidate_id=candidate.candidate_id,
            action=LearningAction.ACCEPT,
            reason="accepted",
            confidence=0.7,
        )
        return LearningWriteProposal(
            proposal_id=proposal_id,
            decision_id=decision.decision_id,
            candidate_id=candidate.candidate_id,
            feedback_id=candidate.feedback_id,
            execution_id=candidate.execution_id,
            handoff_id=candidate.handoff_id,
            tool_name=candidate.tool_name,
            domain=LearningWriteDomain.SEMANTIC,
            payload={"content": "observed success"},
            evidence=candidate.evidence,
            provenance=candidate.provenance,
            confidence=0.7,
            reason="accepted learning decision may proceed to a later learning-write policy",
        )

    def test_admitted_proposal_is_written(self) -> None:
        writer = RecordingWriter(result={"memory_id": 9})
        result = LearningWriteExecutionService(writer).execute(self.admission, self.proposal)
        self.assertEqual(result.status, LearningWriteExecutionStatus.COMPLETED)
        self.assertEqual(result.write_result, {"memory_id": 9})
        self.assertEqual(len(writer.requests), 1)
        self.assertEqual(writer.requests[0].proposal_id, self.proposal.proposal_id)

    def test_failed_writer_becomes_failed_result(self) -> None:
        writer = RecordingWriter(error=RuntimeError("storage unavailable"))
        result = LearningWriteExecutionService(writer).execute(self.admission, self.proposal)
        self.assertEqual(result.status, LearningWriteExecutionStatus.FAILED)
        self.assertIn("storage unavailable", result.reason)

    def test_non_admitted_proposal_cannot_execute(self) -> None:
        rejected = LearningWriteAdmission(
            admission_id="admission-rejected",
            proposal_id=self.proposal.proposal_id,
            decision_id=self.proposal.decision_id,
            candidate_id=self.proposal.candidate_id,
            domain=self.proposal.domain,
            status=LearningWriteAdmissionStatus.REJECTED,
            reason="rejected",
            confidence=0.4,
            policy_id="test-policy",
        )
        writer = RecordingWriter(result=True)
        with self.assertRaises(LearningWriteExecutionError):
            LearningWriteExecutionService(writer).execute(rejected, self.proposal)
        self.assertEqual(writer.requests, [])

    def test_exact_identity_is_required(self) -> None:
        other = self._proposal("proposal-2")
        writer = RecordingWriter(result=True)
        with self.assertRaises(LearningWriteExecutionError):
            LearningWriteExecutionService(writer).execute(self.admission, other)
        self.assertEqual(writer.requests, [])

    def test_execution_id_is_deterministic(self) -> None:
        service = LearningWriteExecutionService(RecordingWriter(result=True))
        first = service.execute(self.admission, self.proposal)
        second = service.execute(self.admission, self.proposal)
        self.assertEqual(first.execution_id, second.execution_id)

    def test_request_preserves_exact_source_identity(self) -> None:
        writer = RecordingWriter(result=True)
        LearningWriteExecutionService(writer).execute(self.admission, self.proposal)
        request = writer.requests[0]
        self.assertEqual(request.admission_id, self.admission.admission_id)
        self.assertEqual(request.proposal_id, self.proposal.proposal_id)
        self.assertEqual(request.decision_id, self.proposal.decision_id)
        self.assertEqual(request.candidate_id, self.proposal.candidate_id)
        self.assertEqual(request.domain, self.proposal.domain.value)

    def test_execution_request_is_immutable(self) -> None:
        writer = RecordingWriter(result=True)
        LearningWriteExecutionService(writer).execute(self.admission, self.proposal)
        with self.assertRaises(FrozenInstanceError):
            writer.requests[0].domain = "meta"  # type: ignore[misc]

    def test_result_is_immutable(self) -> None:
        result = LearningWriteExecutionService(RecordingWriter(result=True)).execute(
            self.admission, self.proposal
        )
        with self.assertRaises(FrozenInstanceError):
            result.status = LearningWriteExecutionStatus.FAILED  # type: ignore[misc]

    def test_result_context_has_no_authority_or_tool_execution(self) -> None:
        result = LearningWriteExecutionService(RecordingWriter(result=True)).execute(
            self.admission, self.proposal
        )
        context = result.to_context()
        self.assertTrue(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_admission_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            LearningWriteExecutionService(RecordingWriter()).execute({}, self.proposal)  # type: ignore[arg-type]

    def test_invalid_proposal_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            LearningWriteExecutionService(RecordingWriter()).execute(self.admission, {})  # type: ignore[arg-type]

    def test_admission_decision_identity_mismatch_is_rejected(self) -> None:
        bad = LearningWriteAdmission(
            admission_id="bad",
            proposal_id=self.proposal.proposal_id,
            decision_id="other-decision",
            candidate_id=self.proposal.candidate_id,
            domain=self.proposal.domain,
            status=LearningWriteAdmissionStatus.ADMITTED,
            reason="test",
            confidence=0.7,
            policy_id="test-policy",
        )
        with self.assertRaises(LearningWriteExecutionError):
            LearningWriteExecutionService(RecordingWriter()).execute(bad, self.proposal)


if __name__ == "__main__":
    unittest.main()
