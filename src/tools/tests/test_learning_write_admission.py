from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.feedback_evaluation import LearningCandidate, LearningSignalKind
from src.tools.learning_decision import LearningAction, LearningDecision
from src.tools.learning_write_admission import (
    DeterministicLearningWriteAdmissionProvider,
    LearningWriteAdmission,
    LearningWriteAdmissionContext,
    LearningWriteAdmissionError,
    LearningWriteAdmissionService,
    LearningWriteAdmissionStatus,
)
from src.tools.learning_write_proposal import LearningWriteDomain, LearningWriteProposal


class LearningWriteAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LearningWriteAdmissionService()

    @staticmethod
    def _candidate() -> LearningCandidate:
        return LearningCandidate(
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

    @classmethod
    def _proposal(
        cls,
        *,
        confidence: float = 0.7,
        payload: dict | None = None,
        evidence: dict | None = None,
        provenance: dict | None = None,
        proposal_id: str = "proposal-1",
    ) -> LearningWriteProposal:
        candidate = cls._candidate()
        decision = LearningDecision(
            decision_id="decision-1",
            candidate_id=candidate.candidate_id,
            action=LearningAction.ACCEPT,
            reason="accepted",
            confidence=confidence,
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
            payload=payload if payload is not None else {"content": "observed success"},
            evidence=evidence if evidence is not None else candidate.evidence,
            provenance=provenance if provenance is not None else candidate.provenance,
            confidence=confidence,
            reason="accepted candidate may proceed",
        )

    def test_complete_proposal_is_admitted(self) -> None:
        result = self.service.admit(LearningWriteAdmissionContext(self._proposal()))
        self.assertEqual(result.status, LearningWriteAdmissionStatus.ADMITTED)
        self.assertTrue(result.admitted)

    def test_empty_payload_is_rejected(self) -> None:
        result = self.service.admit(
            LearningWriteAdmissionContext(self._proposal(payload={}))
        )
        self.assertEqual(result.status, LearningWriteAdmissionStatus.REJECTED)
        self.assertIn("payload", result.reason)

    def test_missing_evidence_is_rejected(self) -> None:
        result = self.service.admit(
            LearningWriteAdmissionContext(self._proposal(evidence={}))
        )
        self.assertEqual(result.status, LearningWriteAdmissionStatus.REJECTED)
        self.assertIn("evidence", result.reason)

    def test_missing_provenance_is_rejected(self) -> None:
        result = self.service.admit(
            LearningWriteAdmissionContext(self._proposal(provenance={}))
        )
        self.assertEqual(result.status, LearningWriteAdmissionStatus.REJECTED)
        self.assertIn("provenance", result.reason)

    def test_low_confidence_is_rejected(self) -> None:
        result = self.service.admit(
            LearningWriteAdmissionContext(self._proposal(confidence=0.49))
        )
        self.assertEqual(result.status, LearningWriteAdmissionStatus.REJECTED)

    def test_admission_preserves_exact_identity(self) -> None:
        proposal = self._proposal()
        result = self.service.admit(LearningWriteAdmissionContext(proposal))
        self.assertEqual(result.proposal_id, proposal.proposal_id)
        self.assertEqual(result.decision_id, proposal.decision_id)
        self.assertEqual(result.candidate_id, proposal.candidate_id)
        self.assertIs(result.domain, proposal.domain)

    def test_admission_id_is_deterministic(self) -> None:
        proposal = self._proposal()
        first = self.service.admit(LearningWriteAdmissionContext(proposal))
        second = self.service.admit(LearningWriteAdmissionContext(proposal))
        self.assertEqual(first.admission_id, second.admission_id)

    def test_admission_is_immutable(self) -> None:
        result = self.service.admit(LearningWriteAdmissionContext(self._proposal()))
        with self.assertRaises(FrozenInstanceError):
            result.status = LearningWriteAdmissionStatus.REJECTED  # type: ignore[misc]

    def test_admission_is_non_authorizing_and_non_writing(self) -> None:
        result = self.service.admit(LearningWriteAdmissionContext(self._proposal()))
        context = result.to_context()
        self.assertFalse(context["learning_write_allowed"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_provider_identity_mismatch_is_rejected(self) -> None:
        proposal = self._proposal()

        class BadProvider(DeterministicLearningWriteAdmissionProvider):
            def admit(self, context):
                return LearningWriteAdmission(
                    admission_id="bad",
                    proposal_id="other",
                    decision_id=proposal.decision_id,
                    candidate_id=proposal.candidate_id,
                    domain=proposal.domain,
                    status=LearningWriteAdmissionStatus.ADMITTED,
                    reason="bad",
                    confidence=0.5,
                    policy_id="bad",
                )

        with self.assertRaises(LearningWriteAdmissionError):
            LearningWriteAdmissionService(BadProvider()).admit(
                LearningWriteAdmissionContext(proposal)
            )

    def test_admission_cannot_grant_write_authority(self) -> None:
        proposal = self._proposal()
        with self.assertRaises(LearningWriteAdmissionError):
            LearningWriteAdmission(
                admission_id="admission-1",
                proposal_id=proposal.proposal_id,
                decision_id=proposal.decision_id,
                candidate_id=proposal.candidate_id,
                domain=proposal.domain,
                status=LearningWriteAdmissionStatus.ADMITTED,
                reason="bad",
                confidence=0.5,
                policy_id="policy",
                learning_write_allowed=True,
            )

    def test_invalid_context_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.admit({"proposal": "bad"})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
