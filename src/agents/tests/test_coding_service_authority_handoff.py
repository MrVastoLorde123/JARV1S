import unittest

from src.agents.authority_handoff import AuthorityHandoffStatus
from src.agents.claim_evidence import Claim, ClaimEvaluation, ClaimState
from src.agents.coding_service import CodingAgentService
from src.agents.consequence_gate import (
    ConsequenceAction,
    ConsequenceKind,
    ConsequenceRequest,
    ConsequenceDecision,
)


class M31CodingServiceAuthorityHandoffTests(unittest.TestCase):
    def _service(self):
        return CodingAgentService(planner=object(), worker=object())

    def _decision(self, action=ConsequenceAction.ALLOW):
        claim = Claim(
            task_id="task-service-31",
            actor="coding_agent",
            payload={"objective": "handoff"},
            provenance={"operation_id": "op-service-31"},
        )
        evaluation = ClaimEvaluation(
            claim=claim,
            state=ClaimState.VERIFIED,
            evidence_refs=("evidence-service-31",),
            verification_refs=("verification-service-31",),
        )
        consequence = ConsequenceRequest(
            kind=ConsequenceKind.ADVANCE_WORKFLOW,
            consequence_id="coding:advance",
        )
        return ConsequenceDecision(
            claim_id=evaluation.claim.claim_id,
            task_id=evaluation.claim.task_id,
            consequence=consequence,
            action=action,
            reason="test decision",
            evidence_refs=evaluation.evidence_refs,
            verification_refs=evaluation.verification_refs,
        )

    def test_service_prepares_ready_handoff_without_authorizing(self):
        handoff = self._service().prepare_authority_handoff(self._decision())
        self.assertEqual(handoff.status, AuthorityHandoffStatus.READY_FOR_AUTHORITY)
        self.assertTrue(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)

    def test_service_preserves_target_and_provenance(self):
        decision = self._decision()
        handoff = self._service().prepare_authority_handoff(
            decision,
            authority_target="coding_confirmation",
        )
        self.assertEqual(handoff.authority_target, "coding_confirmation")
        self.assertEqual(handoff.claim_id, decision.claim_id)
        self.assertEqual(handoff.task_id, decision.task_id)
        self.assertEqual(handoff.evidence_refs, decision.evidence_refs)
        self.assertEqual(handoff.verification_refs, decision.verification_refs)

    def test_service_does_not_turn_review_into_authority_ready(self):
        decision = self._decision(ConsequenceAction.REQUIRE_REVIEW)
        handoff = self._service().prepare_authority_handoff(decision)
        self.assertEqual(handoff.status, AuthorityHandoffStatus.REQUIRE_REVIEW)
        self.assertFalse(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)

    def test_service_does_not_turn_blocked_into_authority_ready(self):
        decision = self._decision(ConsequenceAction.BLOCK)
        handoff = self._service().prepare_authority_handoff(decision)
        self.assertEqual(handoff.status, AuthorityHandoffStatus.BLOCKED)
        self.assertFalse(handoff.ready_for_authority)
        self.assertFalse(handoff.authorized)

    def test_service_rejects_wrong_decision_type(self):
        with self.assertRaises(TypeError):
            self._service().prepare_authority_handoff(object())


if __name__ == "__main__":
    unittest.main()
